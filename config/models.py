from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.
class User(AbstractUser):
    pass


class Server(models.Model):
    class Status(models.IntegerChoices):
        ERROR = 0, 'Error'
        ONLINE = 1, 'Online'

    host = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    is_local_server = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.ONLINE)
    parent_server = models.ForeignKey('Server', models.CASCADE, 'sub_servers', null=True, blank=True)
    auth_key = models.CharField(max_length=128)
    api_port = models.IntegerField(default=8000, null=True, blank=True)
    server_domain = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.host + f' ({self.location})'

    def clean(self):
        super().clean()
        if not self.parent_server and self.auth_key:
            raise ValidationError("Parent servers dont need to auth key!")
        if self.parent_server and not self.auth_key:
            raise ValidationError("Auth key must be filled for sub servers!")


class Log(models.Model):
    class Type(models.IntegerChoices):
        WARNING = 0, 'Warning'
        ERROR = 1, 'Error'

    inbound = models.ForeignKey('inbounds.Inbound', models.CASCADE, 'logs', null=True, blank=True)
    server = models.ForeignKey(Server, models.CASCADE, 'logs', null=True, blank=True)
    inbound_user = models.ForeignKey('inbounds.InboundUser', models.CASCADE, 'logs', null=True, blank=True)

    type = models.PositiveSmallIntegerField(choices=Type.choices)
    solved = models.BooleanField(default=False)
    log_message = models.TextField()
