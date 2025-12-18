# main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
import os
import subprocess

app = FastAPI()

# Carpeta donde se guardan los videos
os.makedirs("static/videos", exist_ok=True)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate/")
async def generate_video(image_url: str = Form(...)):
    """
    image_url: URL de la imagen que quieres poner en el video
    """
    video_template = "template.mp4"  # tu video base
    video_id = str(uuid.uuid4())
    output_path = f"static/videos/{video_id}.mp4"

    # Descargar la imagen temporalmente
    image_path = f"/tmp/{video_id}.png"
    subprocess.run(["curl", "-sL", image_url, "-o", image_path])

    # FFmpeg: mostrar la imagen entre 3.02 y 3.14s
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", video_template,
        "-i", image_path,
        "-filter_complex",
        f"[1:v]format=rgba,fade=in:st=3.02:d=0.12:alpha=1,fade=out:st=3.14:d=0.01:alpha=1[img];[0:v][img]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:format=auto",
        "-c:a", "copy",
        output_path,
        "-y"
    ]
    subprocess.run(ffmpeg_cmd)

    # Borrar la imagen temporal
    os.remove(image_path)

    # Devolver URL directa
    return JSONResponse({
        "video_url": f"https://gatovideo.onrender.com/static/videos/{video_id}.mp4"
    })
