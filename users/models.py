from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from typing import Any

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self,email,password=None,**kwargs):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('Password is required')

        user = self.model(email=self.normalize_email(email).lower(),**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_editor(self,email,password=None,**kwargs: Any) -> Any: 
        kwargs.setdefault('is_editor', True)
        if kwargs.get('is_editor') is not True:
            raise ValueError ('Error! Not an editor')
        return self.create_editor(email, password, **kwargs)

    def create_superuser(
        self, email: str, password: str, **kwargs: Any) -> Any:
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        if not password:
            raise ValueError("Password is required")
        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff (is_staff= True)")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser(is_superuser = True)")
        return self.create_user(email, password, **kwargs)
    

class User(AbstractBaseUser, PermissionsMixin):
        username = models.CharField(max_length=255,unique=True)
        email = models.CharField(max_length=255,unique=True, verbose_name='user email')

        is_active=models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)
        is_editor = models.BooleanField(default=False)
        is_superuser = models.BooleanField(default=False)

        objects = UserManager()
        
        USERNAME_FIELD= 'email' 
        REQUIRED_FIELDS= ['username']

        def __str__(self) -> str:
            return self.email
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="profile_pics", blank=True)
