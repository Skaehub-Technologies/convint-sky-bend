from typing import Any

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from users.abstracts import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **kwargs: Any) -> Any:
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(email=self.normalize_email(email).lower(), **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_editor(self, email: str, password: str, **kwargs: Any) -> Any:
        user = self.create_user(email, password=password, **kwargs)
        user.is_editor = True
        user.save()
        return user

    def create_superuser(
        self, email: str, password: str, **kwargs: Any
    ) -> Any:
        user = self.create_user(email, password=password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    username = models.CharField(max_length=255, unique=True)
    email = models.CharField(
        max_length=255, unique=True, verbose_name="user email"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.email


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    image = CloudinaryField("profile_pics", blank=True)
