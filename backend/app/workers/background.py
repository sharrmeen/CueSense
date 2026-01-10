

from app.models.project import Project
from app.services.renderer import render_video
from app.services.transcriber import transcribe_video
from app.services.brollanalyzer import analyze_broll
from app.services.matcher import generate_edit_plan

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