from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uuid
import os
import subprocess
import requests

app = FastAPI()

video_template = "template.mp4"  # Tu video base
output_dir = "static/videos"

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

# Servir archivos estáticos
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/generate/")
async def generate_video(image_url: str = Query(...)):
    # Descargar imagen
    img_id = str(uuid.uuid4())
    img_path = f"/tmp/{img_id}.png"
    response = requests.get(image_url)
    if response.status_code != 200:
        return JSONResponse({"error": "No se pudo descargar la imagen"}, status_code=400)
    with open(img_path, "wb") as f:
        f.write(response.content)

    # Generar video
    video_id = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"{video_id}.mp4")

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
