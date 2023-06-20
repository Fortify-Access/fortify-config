from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass


class Settings(models.Models):
    pass


class Server(models.Model):
    host = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
