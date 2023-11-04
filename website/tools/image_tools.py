import base64, io
from PIL import Image

def encode_image_to_base64(image: Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return encoded_image