WIDTH = 720 
HEIGHT = 1280

def build_ffmpeg_command(aroll_path, broll_paths, edit_plan, output_path):
    inputs = [f'-i "{aroll_path}"']
    for b_path in broll_paths:
        inputs.append(f'-i "{b_path}"')
    
    filter_parts = []
    last_out = "[0:v]"

    for i, edit in enumerate(edit_plan):
        b_idx = i + 1
        start = edit["start_in_aroll"]
        end = start + edit["duration"]
        
        v_label = f"v{b_idx}"
        v_out = f"v{b_idx}_out"
        filter_parts.append(
            f"[{b_idx}:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},setpts=PTS-STARTPTS+{start}/TB[{v_label}]"
        )
        

        filter_parts.append(f"{last_out}[{v_label}]overlay=x=0:y=0:enable='between(t,{start},{end})'[{v_out}]")
        
        last_out = f"[{v_out}]"

    filter_complex = ";".join(filter_parts)
    

    cmd = [
        "ffmpeg", "-y",
        * " ".join(inputs).split(),
        "-filter_complex", f'"{filter_complex}"',
        "-map", last_out,
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "23", "-c:a", "aac", "-shortest",
        output_path
    ]
    
    return " ".join(cmd)