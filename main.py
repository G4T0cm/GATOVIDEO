from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uuid
import os
import subprocess
import aiohttp
import shutil

app = FastAPI()

video_template = "template.mp4"  # tu video base
output_dir = "static/videos"

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

@app.get("/v/{image_url:path}")
async def generate_video(image_url: str):
    # Descargar la imagen de la URL
    img_id = str(uuid.uuid4())
    img_path = f"/tmp/{img_id}.png"
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                return {"error": "No se pudo descargar la imagen"}
            with open(img_path, "wb") as f:
                f.write(await resp.read())

    # Generar video
    video_id = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"{video_id}.mp4")

    subprocess.run([
        "ffmpeg",
        "-i", video_template,
        "-i", img_path,
        "-filter_complex", "overlay=x=610:y=365:enable='between(t,3.02,3.14)'",
        "-c:a", "copy",
        "-y",  # sobrescribir si existe
        output_path
    ], check=True)

    # Limpiar imagen temporal
    os.remove(img_path)

    # Devolver el video directamente
    return StreamingResponse(
        open(output_path, "rb"),
        media_type="video/mp4"
    )
