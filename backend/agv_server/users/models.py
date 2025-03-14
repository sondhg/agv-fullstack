from django.contrib.auth.models import AbstractUser
from django.db import models

# làm theo https://youtu.be/PUzgZrS_piQ?si=-sonfq6T1UNCSbrt


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    refresh_token = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
