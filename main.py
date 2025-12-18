from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import os
import subprocess
import uuid
import requests

app = FastAPI()

video_template = "template.mp4"  # Tu video base

@app.get("/{folder}/{image_name}.mp4")
def generate_video(folder: str, image_name: str):
    try:
        # Ruta temporal para guardar el video
        video_id = f"{folder}_{image_name}.mp4"
        output_path = f"/tmp/{video_id}"

        # Si ya existe, devolverlo
        if os.path.exists(output_path):
            return FileResponse(output_path, media_type="video/mp4")

        # Descargar la imagen
        img_url = f"https://mudae.net/uploads/{folder}/{image_name}.png"
        img_path = f"/tmp/{uuid.uuid4()}.png"
        resp = requests.get(img_url)
        resp.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(resp.content)

        # Generar video
        subprocess.run([
            "ffmpeg",
            "-i", video_template,
            "-i", img_path,
            "-filter_complex", "overlay=x=610:y=365:enable='between(t,3.02,3.14)'",
            "-c:a", "copy",
            output_path
        ], check=True)

        return FileResponse(output_path, media_type="video/mp4")

    except requests.HTTPError:
        return JSONResponse({"error": "Imagen no encontrada en Mudae"})
    except Exception as e:
        return JSONResponse({"error": str(e)})
