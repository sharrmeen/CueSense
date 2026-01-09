import os
import json
import google.generativeai as genai
from app.models.project import Project

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

async def generate_edit_plan(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    if not project or not project.a_roll:
        return {"error": "project or a-roll data missing"}

    # format transcript with precise timing
    transcript_data = [
        {"start": s["start"], "end": s["end"], "text": s["text"]} 
        for s in project.a_roll.transcript
    ]
    
    # format b-roll inventory with metadata
    broll_inventory = [
        {
            "id": b.broll_id, 
            "description": b.description, 
            "duration": b.duration,
            "keywords": getattr(b, 'keywords', [])
        } 
        for b in project.b_rolls
    ]

    prompt = f"""
    you are an ai video editor. your goal is to enhance a 'talking head' video (a-roll) by strategically inserting b-roll clips based on the transcript.

    input data:
    1. talking head transcript (with timestamps): {json.dumps(transcript_data)}
    2. available b-roll clips: {json.dumps(broll_inventory)}

    editing rules:
    - relevance: only insert a b-roll if the visual description or keywords strongly match the transcript text.
    - timing: the 'start_in_aroll' must align with the beginning of a relevant sentence or phrase.
    - clip duration: do not exceed the actual duration of the b-roll clip.
    - pacing: leave at least 5 seconds between b-roll clips to avoid overwhelming the viewer.
    - output: you must return a valid json array of objects.

    json structure:
    [
      {{
        "broll_id": "string",
        "start_in_aroll": float,
        "duration": float,
        "reason": "brief explanation of why this clip matches this moment"
      }}
    ]
    """

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        edit_plan = json.loads(response.text)
        project.edit_plan = edit_plan
        project.status = "PLAN_READY"
        await project.save()
        return edit_plan
    except Exception as e:
        print(f"failed to parse edit plan: {e}")
        return []