import subprocess
import re

def generate_short_name(title):
    """Generates a short, CamelCase name from a video title."""
    title = re.sub(r'[^a-zA-Z0-9 ]', '', title)
    words = title.split()
    # Limit the number of words to avoid overly long names
    words = words[:5]
    return "".join([word.capitalize() for word in words]) + ".mp4"

def run_ffmpeg(input_path, output_path):
    """Runs the ffmpeg command to downsize a video."""
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vf', "scale='if(gt(iw,ih),-1,360):if(gt(iw,ih),360,-1)'",
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path}:")
        print(e.stderr)
        return False

def update_logs(video_info):
    """Logs processed video information to logs.txt."""
    with open("logs.txt", "a") as f:
        f.write(f"{video_info}\n")
