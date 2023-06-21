from django.db import models

# Create your models here.
class Inbound(models.Model):
    server = models.ForeignKey('config.Server', models.CASCADE, 'inbounds')
    remark = models.CharField(max_length=64)
    port = models.IntegerField()
    expiration_date = models.DateTimeField(null=True, blank=True)


class TrafficUsage(models.Model):
    inbound = models.OneToOneField(Inbound, models.CASCADE, related_name='traffic_usage')
    upload = models.BigIntegerField()
    download = models.BigIntegerField()
