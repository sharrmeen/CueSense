import os
import uuid
import io
from typing import List
from fastapi import APIRouter, UploadFile, File, Query, HTTPException,BackgroundTasks
from app.models.project import Project, ARoll, BRoll
from app.utils.storage import client, BUCKET_A_ROLL, BUCKET_B_ROLL
from backend.app.services.transcriber import transcribe_video 

router = APIRouter()

@router.post("/create-project")
async def create_project(name:str):
    project_id = str(uuid.uuid4().hex[:6]).upper()
    new_project = Project(project_id=project_id,name=name)
    await new_project.insert()
    return {"project_id": project_id}

@router.post("/a-roll")
async def upload_a_roll(project_id: str = Query(...), file: UploadFile = File(...)):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_ext = os.path.splitext(file.filename)[1]
    file_id = f"aroll_{uuid.uuid4().hex[:8]}{file_ext}"

    try:
        # stream data to minio
        file_data = await file.read()
        client.put_object(
            BUCKET_A_ROLL, 
            file_id, 
            io.BytesIO(file_data), 
            length=len(file_data),
            content_type=file.content_type
        )

        # Update MongoDB with the same ID
        project.a_roll = ARoll(file_id=file_id, path=file_id)
        project.status = "A_ROLL_UPLOADED"
        await project.save()

        return {"file_id": file_id, "status": "Uploaded and Linked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/b-roll")
async def upload_multiple_b_rolls(
    project_id: str = Query(...), 
    files: List[UploadFile] = File(...)  # Accept a list of files
):
    project = await Project.find_one(Project.project_id == project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    uploaded_ids = []
    
    for file in files:
        
        file_ext = os.path.splitext(file.filename)[1]
        broll_id = f"broll_{uuid.uuid4().hex[:8]}{file_ext}"

        try:
            
            file_data = await file.read()
            client.put_object(
                BUCKET_B_ROLL, 
                broll_id, 
                io.BytesIO(file_data), 
                length=len(file_data),
                content_type=file.content_type
            )

            
            new_broll = BRoll(broll_id=broll_id, path=broll_id, duration=0.0)
            project.b_rolls.append(new_broll)
            uploaded_ids.append(broll_id)
            
        except Exception as e:
            print(f"Failed to upload {file.filename}: {e}")

    
    await project.save()

    return {
        "status": f"Successfully uploaded {len(uploaded_ids)} B-Rolls",
        "broll_ids": uploaded_ids,
        "total_clips": len(project.b_rolls)
    }
    
    
@router.post("/{project_id}/process")
async def start_processing(project_id: str, background_tasks: BackgroundTasks):
    project = await Project.find_one(Project.project_id == project_id)
    if not project or not project.a_roll:
        raise HTTPException(status_code=400, detail="A-Roll missing")

    # Update status immediately
    project.status = "TRANSCRIBING"
    await project.save()

    # Trigger background task
    background_tasks.add_task(run_transcription_pipeline, project_id)
    
    return {"message": "Transcription started"}

async def run_transcription_pipeline(project_id: str):
    """The background worker logic."""
    project = await Project.find_one(Project.project_id == project_id)
    
    try:
        
        segments = await transcribe_video(project.a_roll.file_id)
        
        project.a_roll.transcript = segments
        project.status = "TRANSCRIPTION_COMPLETE"
        await project.save()
        print(f"Project {project_id} transcribed successfully")
        
    except Exception as e:
        project.status = "FAILED"
        await project.save()
        print(f"Transcription failed for {project_id}: {str(e)}")