from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import uuid
import hashlib
import subprocess
import requests

app = FastAPI()

video_template = "template.mp4"  # Tu video base
output_dir = "static/videos"
os.makedirs(output_dir, exist_ok=True)

def hash_url(url: str) -> str:
    """Crea un hash corto para usar como nombre de archivo único."""
    return hashlib.md5(url.encode()).hexdigest()

@app.get("/v/{url:path}")
def video_from_url(url: str):
    try:
        # Nombre del video basado en hash de la URL
        video_name = f"{hash_url(url)}.mp4"
        output_path = os.path.join(output_dir, video_name)

        # Si el video ya existe, devolverlo directamente
        if os.path.exists(output_path):
            return FileResponse(output_path, media_type="video/mp4")

        # Descargar la imagen
        img_path = f"/tmp/{uuid.uuid4()}.png"
        resp = requests.get(url)
        resp.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(resp.content)

        # Generar el video con FFmpeg
        subprocess.run([
            "ffmpeg",
            "-i", video_template,
            "-i", img_path,
            "-filter_complex", "overlay=x=610:y=365:enable='between(t,3.02,3.14)'",
            "-c:a", "copy",
            output_path
        ], check=True)

        # Devolver el archivo generado
        return FileResponse(output_path, media_type="video/mp4")

    except Exception as e:
        return {"error": str(e)}
