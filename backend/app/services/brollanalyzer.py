import os
import tempfile
import time
import json
import asyncio
import google.generativeai as genai
from app.utils.storage import client, BUCKET_B_ROLL
from dotenv import load_dotenv
load_dotenv()


# setup gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash") 

async def analyze_broll(broll_id: str):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        try:
            # fetch from minio
            response = client.get_object(BUCKET_B_ROLL, broll_id)
            temp_file.write(response.read())
            temp_file.flush()

            # upload to gemini api
            video_file = genai.upload_file(path=temp_file.name)

            # wait for processing 
            while video_file.state.name == "PROCESSING":
                await asyncio.sleep(2)
                video_file = genai.get_file(video_file.name)

            # strict prompt for structured output
            prompt = """
            analyze this video clip for a b-roll matching system.
            return a json object with the following keys:
            - description: a concise one-sentence visual summary.
            - keywords: a list of 5 search terms based on objects and actions.
            - mood: a single word describing the vibe (e.g., professional, energetic, calm).
            """

            # generation_config to force json output
            response = model.generate_content(
                [prompt, video_file],
                generation_config={"response_mime_type": "application/json"}
            )
            
            genai.delete_file(video_file.name)
            
            # parse string into a python dictionary
            return json.loads(response.text)

        except Exception as e:
            print(f"error analyzing {broll_id}: {str(e)}")
            return {
                "description": "analysis failed",
                "keywords": [],
                "mood": "unknown"
            }
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)