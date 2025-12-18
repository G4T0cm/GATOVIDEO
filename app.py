from fastapi import FastAPI
from fastapi.responses import FileResponse
import subprocess
import uuid
import requests
import os
import urllib.parse

app = FastAPI()

# Carpeta para videos generados
os.makedirs("videos", exist_ok=True)

@app.get("/v/{img_url:path}")
def generate_video(img_url: str):
    img_url = urllib.parse.unquote(img_url)

    img_tmp = f"/tmp/{uuid.uuid4()}.png"
    out_mp4 = f"videos/{uuid.uuid4()}.mp4"

    # Descargar imagen desde la URL
    r = requests.get(img_url, timeout=10)
    with open(img_tmp, "wb") as f:
        f.write(r.content)

    # Generar vídeo con FFmpeg
    subprocess.run([
        "ffmpeg", "-y",
        "-i", "template.mp4",
        "-i", img_tmp,
        "-filter_complex", "overlay=100:100:enable='between(t,3.02,3.14)'",
        "-movflags", "+faststart",
        out_mp4
    ], check=True)

    # Devolver el MP4 directamente para Discord
    return FileResponse(out_mp4, media_type="video/mp4")
