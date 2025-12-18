from fastapi import FastAPI, Path
from fastapi.responses import FileResponse
import uuid
import os
import subprocess
import requests

app = FastAPI()

video_template = "template.mp4"
output_dir = "static/videos"
os.makedirs(output_dir, exist_ok=True)

@app.get("/v/{image_url:path}")
async def generate_video(image_url: str = Path(...)):
    import urllib.parse
    image_url = urllib.parse.unquote(image_url)

    # Descargar imagen
    img_id = str(uuid.uuid4())
    img_path = f"/tmp/{img_id}.png"
    response = requests.get(image_url)
    if response.status_code != 200:
        return {"error": "No se pudo descargar la imagen"}
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

    # Devolver el archivo directamente para Discord
    return FileResponse(output_path, media_type="video/mp4", filename=f"{video_id}.mp4")
