from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass


class Server(models.Model):
    host = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    is_local_server = models.BooleanField(default=False)
    incoming_port = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.host + f' ({self.location})'

    def clean(self):
        super().clean()
        if hasattr(self, 'dns') and not self.incoming_port:
            raise models.ValidationError("Incoming port can be empty when server has a cloudflare dns!")


class CloudFlareDNS(models.Model):
    server = models.OneToOneField(Server, models.PROTECT, related_name='dns')
    zone_id = models.CharField(max_length=128)
    token = models.CharField(max_length=128)
    original_domain = models.CharField(max_length=64)


class Log(models.Model):
    class Type(models.IntegerChoices):
        WARNING = 0, 'Warning'
        ERROR = 1, 'Error'

    inbound = models.ForeignKey('inbounds.Inbound', models.CASCADE, 'logs', null=True, blank=True)
    server = models.ForeignKey(Server, models.CASCADE, 'logs', null=True, blank=True)
    inbound_user = models.ForeignKey('inbounds.InboundUser', models.CASCADE, 'logs', null=True, blank=True)
    cloudflare_dns = models.ForeignKey(CloudFlareDNS, models.CASCADE, 'logs', null=True, blank=True)

    type = models.PositiveSmallIntegerField(choices=Type.choices)
    solved = models.BooleanField(default=False)
    log_message = models.TextField()
