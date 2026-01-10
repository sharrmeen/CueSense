import os
import json
import google.generativeai as genai
from app.models.project import Project

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

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
            "keywords": getattr(b, 'keywords', []),
            "mood": getattr(b, 'mood', 'neutral')
            
        } 
        for b in project.b_rolls
    ]

    prompt = f"""
            ROLE: You are an expert Video Editor with 10+ years of experience in 'Talking Head' content and B-Roll sequencing.

            TASK:
            Match provided B-Roll clips to the A-Roll transcript to create a visually engaging narrative. 
            Return ONLY a valid JSON array of objects.

            INPUT DATA:
            - Transcript: {json.dumps(transcript_data)}
            - B-Roll Inventory: {json.dumps(broll_inventory)}

            EDITORIAL STANDARDS:
            1. SEMANTIC MATCHING: Look for direct keyword matches (e.g., 'Coffee') and conceptual matches (e.g., 'Morning routine' for a clip of someone waking up).
            2. DENSITY: Aim for a match every 8-12 seconds if the inventory allows. Do not settle for just one match if multiple relevant clips are available.
            3. MINIMUM GAP: Maintain at least 2.5 seconds between the end of one B-roll and the start of the next to ensure the speaker's face is still visible.
            4. DURATION ADHERENCE: 'duration' in your output MUST NOT exceed the 'duration' provided in the B-Roll Inventory for that clip.
            5. REASONING: Provide a clear, professional justification for every match.

            OUTPUT FORMAT (JSON):
            [
            {{
                "broll_id": "string",
                "start_in_aroll": float,
                "duration": float,
                "reason": "Explicitly explain why this visual enhances the spoken words at this timestamp"
            }}
            ]

            EXAMPLE:
            If transcript says "I started my business in a small garage," and B-roll 'broll_123' shows a cluttered workspace, match it at the timestamp of 'small garage'.
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