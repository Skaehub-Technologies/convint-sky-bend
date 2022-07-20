from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image

fake = Faker()


def sample_image() -> SimpleUploadedFile:
    image_file = BytesIO()
    image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
    image.save(image_file, "png")
    image_file.seek(0)
    return SimpleUploadedFile(
        "test.png", image_file.read(), content_type="image/png"
    )


def sample_data() -> dict:
    return {
        "title": fake.name(),
        "description": fake.text(),
        "body": fake.text(),
        "image": sample_image(),
        "is_hidden": False,
        "tags": f'["{fake.word()}", "{fake.word()}"]',
        "favorited": False,
        "favoritesCount": 0,
    }
