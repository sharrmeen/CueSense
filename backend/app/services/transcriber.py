import os
import tempfile
from faster_whisper import WhisperModel
from app.utils.storage import client, BUCKET_A_ROLL

model = WhisperModel("base", device="cpu", compute_type="float32")

async def transcribe_video(file_id: str):
    """
    Downloads video from MinIO and transcribes locally using Faster-Whisper.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        try:
            #Download from MinIO
            response = client.get_object(BUCKET_A_ROLL, file_id)
            temp_video.write(response.read())
            temp_video.flush()
            
            #Run Local Transcription
            segments, info = model.transcribe(temp_video.name, vad_filter=True)
            
            #Format segments for our Matching Engine
            formatted_segments = [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                for segment in segments
            ]
            
            return formatted_segments

        finally:
            if os.path.exists(temp_video.name):
                os.remove(temp_video.name)