from django.db import models

# Create your models here.
class TrafficUsage(models.Model):
    pass


class Inbound(models.Model):
    remark = models.CharField(max_length=64)
    port = models.IntegerField()
    expiration_date = models.DateTimeField(null=True, blank=True)
