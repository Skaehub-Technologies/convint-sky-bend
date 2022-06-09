from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('Password is required')

        user = self.model(email=self.normalize_email(email).lower(),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_editor(self,email,password=None,**extra_fields): 
        user =self.create_user(email,password=password,**extra_fields)
        user.is_editor=True
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):  
        user =self.create_user(email,password=password,**extra_fields)
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class User(AbstractUser):
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
    
