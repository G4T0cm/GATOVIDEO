from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
import os
import subprocess

app = FastAPI()

video_template = "template.mp4"  # Tu video base
output_dir = "static/videos"

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

@app.post("/generate/")
async def generate_video(image: UploadFile = File(...)):
    # Guardar imagen temporal
    img_id = str(uuid.uuid4())
    img_path = f"/tmp/{img_id}.png"
    with open(img_path, "wb") as f:
        f.write(await image.read())

    # Generar video
    video_id = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"{video_id}.mp4")

    # FFmpeg overlay
    subprocess.run([
        "ffmpeg",
        "-i", video_template,
        "-i", img_path,
        "-filter_complex", "overlay=x=610:y=365:enable='between(t,3.02,3.14)'",
        "-c:a", "copy",
        output_path
    ], check=True)

    return JSONResponse({
        "video_url": f"https://gatovideo.onrender.com/static/videos/{video_id}.mp4"
    })
