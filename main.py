from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import uuid, subprocess, os, requests

app = FastAPI()

video_template = "template.mp4"  # tu video base

@app.get("/{folder}/{image_name}.mp4")
def generate_video(folder: str, image_name: str):
    try:
        # Nombre del video y ruta temporal
        video_file = f"{folder}_{image_name}.mp4"
        video_path = f"/tmp/{video_file}"

        # Si ya existe, devolverlo directamente
        if os.path.exists(video_path):
            return FileResponse(video_path, media_type="video/mp4")

        # Descargar la imagen desde Mudae
        img_url = f"https://mudae.net/uploads/{folder}/{image_name}.png"
        img_path = f"/tmp/{uuid.uuid4()}.png"
        resp = requests.get(img_url)
        resp.raise_for_status()
        with open(img_path, "wb") as f:
            f.write(resp.content)

        # Generar video con FFmpeg
        subprocess.run([
            "ffmpeg",
            "-y",  # sobrescribir si existe
            "-i", video_template,
            "-i", img_path,
            "-filter_complex", "overlay=x=610:y=365:enable='between(t,3.02,3.14)'",
            "-c:a", "copy",
            video_path
        ], check=True)

        return FileResponse(video_path, media_type="video/mp4")

    except requests.HTTPError:
        return JSONResponse({"error": "Imagen no encontrada en Mudae"})
    except Exception as e:
        return JSONResponse({"error": str(e)})
