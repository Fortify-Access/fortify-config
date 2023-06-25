from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass


class Settings(models.Model):
    sing_box_binary_path = models.CharField(max_length=364)


class Server(models.Model):
    host = models.CharField(max_length=128)
    location = models.CharField(max_length=128)

    def __str__(self):
        return self.host + f' ({self.location})'
