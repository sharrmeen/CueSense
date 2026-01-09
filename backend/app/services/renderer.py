import os
import subprocess
import tempfile
from app.utils.storage import client, BUCKET_A_ROLL, BUCKET_B_ROLL
from app.models.project import Project

async def render_video(project_id: str):
    project = await Project.find_one(Project.project_id == project_id)
    if not project or not project.edit_plan:
        return None

    # create a workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        aroll_path = os.path.join(tmp_dir, "aroll.mp4")
        output_path = f"outputs/{project_id}_final.mp4"
        os.makedirs("outputs", exist_ok=True)

        # download a-roll
        aroll_data = client.get_object(BUCKET_A_ROLL, project.a_roll.file_id)
        with open(aroll_path, "wb") as f:
            f.write(aroll_data.read())

        # build the ffmpeg filter complex
        input_files = ["-i", aroll_path]
        filter_parts = []
        last_label = "[0:v]"

        for i, edit in enumerate(project.edit_plan):
            broll_id = edit["broll_id"]
            start = edit["start_in_aroll"]
            duration = edit["duration"]
            end = start + duration
            
            # download each b-roll used in the plan
            b_path = os.path.join(tmp_dir, f"b_{i}.mp4")
            b_data = client.get_object(BUCKET_B_ROLL, broll_id)
            with open(b_path, "wb") as f:
                f.write(b_data.read())
            
            input_files.extend(["-i", b_path])
            
            #scale b-roll to match a-roll (720p)
            label = f"v{i+1}"
            filter_parts.append(
                f"[{i+1}:v]scale=1280:720,setpts=PTS-STARTPTS+{start}/TB[{label}];"
                f"{last_label}[{label}]overlay=enable='between(t,{start},{end})'[{label}_out]"
            )
            last_label = f"[{label}_out]"

        #combine all parts into the final command
        filter_complex = "".join(filter_parts)
        
        cmd = [
            "ffmpeg", "-y",
            *input_files,
            "-filter_complex", filter_complex,
            "-map", last_label,
            "-map", "0:a", 
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "aac",
            output_path
        ]

        #run ffmpeg
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if process.returncode != 0:
            print(f"ffmpeg error: {process.stderr}")
            project.status = "RENDER_FAILED"
            await project.save()
            return None

        project.status = "COMPLETED"
        project.final_video_path = output_path
        await project.save()
        return output_path