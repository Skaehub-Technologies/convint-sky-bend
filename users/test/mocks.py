from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image

fake = Faker()

test_user = {
    "username": fake.name(),
    "email": fake.email(),
    "password": fake.password(),
}

image_file = BytesIO()
image = Image.new("RGBA", size=(50, 50), color=(256, 0, 0))
image.save(image_file, "png")
image_file.seek(0)

test_image = SimpleUploadedFile(
    "test.png", image_file.read(), content_type="image/png"
)

test_user_2 = {
    "username": fake.user_name(),
    "password": fake.password(),
    "email": fake.email(),
}
