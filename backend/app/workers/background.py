

from backend.app.models.project import Project
from backend.app.services.renderer import render_video
from backend.app.services.transcriber import transcribe_video

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