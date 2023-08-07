from django.db import models
from django.contrib.auth.models import AbstractUser

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
    parent_server = models.ForeignKey('Server', models.CASCADE, 'subservers', null=True, blank=True)
    auth_key = models.CharField(max_length=128, null=True, blank=True)
    api_port = models.IntegerField(default=8000, null=True, blank=True)
    redis_port = models.IntegerField(unique=True, null=True, blank=True)
    server_domain = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.host + f' ({self.location})'

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=models.Q(parent_server__isnull=True, redis_port__isnull=False) | models.Q(parent_server__isnull=False, redis_port__isnull=True),
                name='check_redis_port'),
            models.CheckConstraint(
                check=models.Q(parent_server__isnull=False, auth_key__isnull=False) | models.Q(parent_server__isnull=True, auth_key__isnull=True),
                name='check_subserver_auth_key'),
        )


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
