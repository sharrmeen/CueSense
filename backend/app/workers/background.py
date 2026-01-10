import os
import secrets
import subprocess
import tempfile
from app.models.project import Project
from app.services.transcriber import transcribe_video
from app.services.brollanalyzer import analyze_broll
from app.services.matcher import generate_edit_plan
from app.services.renderer import build_ffmpeg_command
from app.utils.storage import client,BUCKET_A_ROLL, BUCKET_B_ROLL, BUCKET_OUTPUTS

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

# # background logic for gemini analysis and matching
# async def run_full_analysis_and_matching(project_id: str):
#     from app.services.brollanalyzer import analyze_broll
#     from app.services.matcher import generate_edit_plan

#     project = await Project.find_one(Project.project_id == project_id)
    
#     try:
#         for broll in project.b_rolls:
#             if not broll.description:
#                 analysis = await analyze_broll(broll.broll_id)
#                 broll.description = analysis.get("description")
#                 broll.keywords = analysis.get("keywords",[])
#                 broll.mood = analysis.get("mood", "neutral")
        
#         await project.save()
        
#         project.status = "MATCHING_CLIPS"
#         await project.save()
        
#         await generate_edit_plan(project_id)

#     except Exception as e:
#         project.status = "FAILED"
#         await project.save()
#         print(f"matching failed for {project_id}: {str(e)}")
        
        
# async def run_broll_analysis(project_id: str):
#     project = await Project.find_one(Project.project_id == project_id)
#     print(f"DEBUG: Found {len(project.b_rolls)} clips in DB for analysis.")
#     project.status = "ANALYZING_BROLL"
#     await project.save()

#     for broll in project.b_rolls:
#         if not broll.description:
#             analysis = await analyze_broll(broll.broll_id)
#             broll.description = analysis.get("description")
#             broll.keywords = analysis.get("keywords", [])
#             broll.mood = analysis.get("mood", "neutral")
#             await project.save()

   
#     project.status = "BROLL_ANALYZED"
#     await project.save()

async def run_broll_analysis(project_id: str):
    
    project = await Project.find_one(Project.project_id == project_id)
    total_clips = len(project.b_rolls)
    
    print(f"DEBUG: Found {len(project.b_rolls)} clips in DB for analysis.") 

    if not project.b_rolls:
        print("DEBUG: Logic skipped because b_rolls list is empty.") 
        return

    try:
        project.status = "ANALYZING_BROLL"
        await project.save()

        for i, broll in enumerate(project.b_rolls):
            print(f"DEBUG: Starting Gemini analysis for clip {i+1}/{len(project.b_rolls)}: {broll.broll_id}") 
            project.status_message = f"Starting Gemini analysis for clip {i+1}/{total_clips}"
            await project.save()
            
            
            if broll.description in [None, "No description available"]:
                analysis = await analyze_broll(broll.broll_id)
                broll.description = analysis.get("description")
                broll.keywords = analysis.get("keywords", [])
                broll.mood = analysis.get("mood", "neutral")
                project.b_rolls[i] = broll
                await project.save()
                print(f"DEBUG: Successfully analyzed {broll.broll_id}") 
            else:
                print(f"DEBUG: Skipping {broll.broll_id} (already has description)") 

        
        project.status = "BROLL_ANALYZED"
        project.status_message = "All clips analyzed successfully."
        await project.save()
        print("DEBUG: Analysis phase complete. Status set to BROLL_ANALYZED.") 

    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR during analysis: {str(e)}") 
        project.status = "FAILED"
        await project.save()

async def run_matching_logic(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    project.status = "MATCHING_CLIPS"
    await project.save()
    await generate_edit_plan(project_id)
        

async def run_video_render(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    if not project or not project.edit_plan:
        return

    try:
        project.status = "RENDERING"
        project.status_message = "Preparing workspace..."
        await project.save()

        with tempfile.TemporaryDirectory() as tmp_dir:
            #Download A-Roll
            aroll_path = os.path.join(tmp_dir, "aroll.mp4")
            aroll_data = client.get_object(BUCKET_A_ROLL, project.a_roll.file_id)
            with open(aroll_path, "wb") as f:
                f.write(aroll_data.read())

            # Download B-Rolls used in plan
            local_broll_paths = []
            for i, edit in enumerate(project.edit_plan):
                project.status_message = f"Downloading assets for clip {i+1}..."
                await project.save()
                
                b_path = os.path.join(tmp_dir, f"b_{i}.mp4")
                b_data = client.get_object(BUCKET_B_ROLL, edit["broll_id"])
                with open(b_path, "wb") as f:
                    f.write(b_data.read())
                local_broll_paths.append(b_path)

            #Execute Render
            local_output = os.path.join(tmp_dir, "final_render.mp4")
            project.status_message = "Executing FFmpeg render engine..."
            await project.save()

            cmd = build_ffmpeg_command(aroll_path, local_broll_paths, project.edit_plan, local_output)
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if process.returncode != 0:
                raise Exception(f"FFmpeg failed: {process.stderr}")

            #Upload Result to MinIO
            project.status_message = "Uploading final video to cloud..."
            await project.save()
            random_suffix = secrets.token_hex(3)
            minio_path = f"{project_id}/final_master_{random_suffix}.mp4"
            with open(local_output, "rb") as f:
                client.put_object(BUCKET_OUTPUTS, minio_path, f, os.path.getsize(local_output))

            project.status = "COMPLETED"
            project.status_message = "Render successful!"
            project.final_video_path = minio_path 
            await project.save()

    except Exception as e:
        print(f"Render Task Failed: {str(e)}")
        project.status = "FAILED"
        project.status_message = f"Render Error: {str(e)}"
        await project.save()