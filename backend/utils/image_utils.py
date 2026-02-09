from PIL import Image
import io
import base64

def generate_thumbnail(image_bytes, size=(128, 128)):
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(size)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    return base64.b64encode(buffer.getvalue()).decode()
