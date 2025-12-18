from fastapi import FastAPI
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

@app.get("/v/{url:path}")
def video_from_url(url: str):
    try:
        # Descargar la imagen remota
        img_id = str(uuid.uuid4())
        img_path = f"/tmp/{img_id}.png"
        resp = requests.get(url)
        resp.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(resp.content)

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

        # Devolver URL pública terminada en .mp4
        video_url = f"https://gatovideo.onrender.com/static/videos/{video_id}.mp4"
        return JSONResponse({"url": video_url})

    except Exception as e:
        return {"error": str(e)}
