from flask import current_app
import requests
from os import path
import io
import uuid
from PIL import Image

from .. import AppConst

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

diffusion_container_path = "/diffusion"

def diffusion_compute(prompt: str) -> str:
    if len(prompt) == 0:
        prompt = "An astronaut riding a green horse"

    print("Start generating...")
    headers = {f"\"Authorization\": \"Bearer {current_app.config[AppConst.CONFIG_HUGGINGFACE_API_KEY]}\""}
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    image_bytes = response.content
    print("Generation complete!")

    image = Image.open(io.BytesIO(image_bytes))

    container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH] + diffusion_container_path
    uid = str(uuid.uuid4())
    result_image_path = path.join(container_path, f"diffusion_result_{uid}.jpg")
    with open(result_image_path, "w") as f:
        image.save(f, format="JPEG")

    return result_image_path

        