import os
import uuid
import io
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.models.project import Project, ARoll, BRoll
from app.utils.storage import client, BUCKET_A_ROLL, BUCKET_B_ROLL
from backend.app.services.renderer import render_video
from backend.app.services.transcriber import transcribe_video
from backend.app.utils.video import get_video_duration 

router = APIRouter()

# initializes a new project and returns a unique short id
@router.post("/create-project")
async def create_project(name: str):
    project_id = str(uuid.uuid4().hex[:6]).upper()
    new_project = Project(project_id=project_id, name=name)
    await new_project.insert()
    return {"project_id": project_id}

# handles a-roll upload, extracts duration, and triggers transcription
@router.post("/a-roll")
async def upload_a_roll(
    background_tasks: BackgroundTasks,
    project_id: str = Query(...), 
    file: UploadFile = File(...)
):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    file_ext = os.path.splitext(file.filename)[1]
    file_id = f"aroll_{uuid.uuid4().hex[:8]}{file_ext}"

    try:
        file_data = await file.read()

        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name
        
        duration = get_video_duration(tmp_path)
        os.remove(tmp_path)

        client.put_object(
            BUCKET_A_ROLL, 
            file_id, 
            io.BytesIO(file_data), 
            length=len(file_data),
            content_type=file.content_type
        )

        project.a_roll = ARoll(file_id=file_id, path=file_id, duration=duration)
        project.status = "TRANSCRIBING"
        await project.save()

        background_tasks.add_task(run_transcription_pipeline, project_id)

        return {
            "file_id": file_id, 
            "duration": duration,
            "status": "upload complete, transcription started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upload failed: {str(e)}")

# accepts multiple b-roll files and saves them with their durations
@router.post("/b-roll")
async def upload_multiple_b_rolls(
    project_id: str = Query(...), 
    files: List[UploadFile] = File(...)
):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    uploaded_ids = []
    
    for file in files:
        file_ext = os.path.splitext(file.filename)[1]
        broll_id = f"broll_{uuid.uuid4().hex[:8]}{file_ext}"

        try:
            file_data = await file.read()

            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name
            
            duration = get_video_duration(tmp_path)
            os.remove(tmp_path)

            client.put_object(
                BUCKET_B_ROLL, 
                broll_id, 
                io.BytesIO(file_data), 
                length=len(file_data),
                content_type=file.content_type
            )
            
            new_broll = BRoll(broll_id=broll_id, path=broll_id, duration=duration)
            project.b_rolls.append(new_broll)
            uploaded_ids.append(broll_id)
            
        except Exception as e:
            print(f"failed to upload {file.filename}: {e}")

    await project.save()

    return {
        "status": f"successfully uploaded {len(uploaded_ids)} b-rolls",
        "broll_ids": uploaded_ids,
        "total_clips": len(project.b_rolls)
    }

# returns the current state and metadata of the project for polling
@router.get("/{project_id}/status")
async def get_project_status(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    return {
        "project_id": project.project_id,
        "status": project.status,
        "a_roll_duration": project.a_roll.duration if project.a_roll else 0,
        "b_roll_count": len(project.b_rolls)
    }

# kicks off the gemini analysis of clips and the edit plan generation
@router.post("/{project_id}/generate-edit-plan")
async def start_matching_process(project_id: str, background_tasks: BackgroundTasks):
    project = await Project.find_one(Project.project_id == project_id)
    
    if not project or project.status != "TRANSCRIPTION_COMPLETE":
        raise HTTPException(status_code=400, detail="transcription must be complete first")

    if not project.b_rolls:
        raise HTTPException(status_code=400, detail="upload b-rolls first")

    project.status = "ANALYZING_BROLLS"
    await project.save()

    background_tasks.add_task(run_full_analysis_and_matching, project_id)
    
    return {"message": "analysis and matching started", "project_id": project_id}

# starts the ffmpeg rendering process once the edit plan is ready
@router.post("/{project_id}/render")
async def start_rendering(project_id: str, background_tasks: BackgroundTasks):
    project = await Project.find_one(Project.project_id == project_id)
    
    if not project or project.status != "PLAN_READY":
        raise HTTPException(
            status_code=400, 
            detail="edit plan must be generated before rendering"
        )

    project.status = "RENDERING"
    await project.save()

    background_tasks.add_task(run_render_task, project_id)
    
    return {"message": "rendering started", "project_id": project_id}

# allows the user to download the final rendered video file
@router.get("/{project_id}/download")
async def download_video(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    
    if not project or project.status != "COMPLETED":
        raise HTTPException(status_code=404, detail="video not ready or not found")

    if not os.path.exists(project.final_video_path):
        raise HTTPException(status_code=404, detail="file missing on server")

    return FileResponse(
        path=project.final_video_path, 
        filename=f"final_{project_id}.mp4",
        media_type="video/mp4"
    )

# background logic for a-roll transcription
async def run_transcription_pipeline(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        return
    
    try:
        segments = await transcribe_video(project.a_roll.file_id)
        project.a_roll.transcript = segments
        project.status = "TRANSCRIPTION_COMPLETE"
        await project.save()
    except Exception as e:
        print(f"transcription error: {e}")
        project.status = "FAILED"
        await project.save()

# background logic for gemini analysis and matching
async def run_full_analysis_and_matching(project_id: str):
    from app.services.brollanalyzer import analyze_broll
    from app.services.matcher import generate_edit_plan

    project = await Project.find_one(Project.project_id == project_id)
    
    try:
        for broll in project.b_rolls:
            if not broll.description:
                analysis = await analyze_broll(broll.broll_id)
                broll.description = analysis.get("description")
                broll.keywords = analysis.get("keywords")
        
        await project.save()
        
        project.status = "MATCHING_CLIPS"
        await project.save()
        
        await generate_edit_plan(project_id)

    except Exception as e:
        project.status = "FAILED"
        await project.save()
        print(f"matching failed for {project_id}: {str(e)}")

# background logic for executing ffmpeg
async def run_render_task(project_id: str):
    try:
        output_path = await render_video(project_id)
        if output_path:
            print(f"render successful: {output_path}")
        else:
            print(f"render failed for {project_id}")
    except Exception as e:
        project = await Project.find_one(Project.project_id == project_id)
        if project:
            project.status = "FAILED"
            await project.save()
        print(f"rendering error: {e}")