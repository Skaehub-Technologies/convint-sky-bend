from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def sample_image() -> SimpleUploadedFile:
    image_file = BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
    image.save(image_file, "png")
    image_file.seek(0)
    return SimpleUploadedFile(
        "test.png", image_file.read(), content_type="image/png"
    )
