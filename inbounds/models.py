from django.db import models
from django.core.exceptions import ValidationError
from . import functions

# Create your models here.
class Inbound(models.Model):
    class Type(models.TextChoices):
        VMESS = 'vmess', 'vmess'
        VLESS = 'vless', 'vless'

    class DomainStrategy(models.TextChoices):
        PREFER_IPV4 = 'prefer_ipv4', 'Prefer IPV4'
        PREFER_IPV6 = 'prefer_ipv6', 'Prefer IPV6'
        IPV4_ONLY = 'ipv4_only', 'IPV4 Only'
        IPV6_ONLY = 'ipv6_only', 'IPV6 Only'

    server = models.ForeignKey('config.Server', models.CASCADE, 'inbounds')
    type = models.CharField(max_length=5, choices=Type.choices)
    tag = models.CharField(max_length=64)
    listen = models.CharField(max_length=36, default='::')
    listen_port = models.IntegerField(unique=True)
    tcp_fast_open = models.BooleanField()
    udp_fragment = models.BooleanField()
    sniff = models.BooleanField()
    sniff_override_destination = models.BooleanField()
    sniff_timeout = models.IntegerField(null=True, blank=True, help_text='ms')
    domain_strategy = models.CharField(max_length=11, choices=DomainStrategy.choices, null=True, blank=True)
    udp_timeout = models.IntegerField(null=True, blank=True)
    proxy_protocol = models.BooleanField()
    proxy_protocol_accept_no_header = models.BooleanField()

    def __str__(self):
        return self.server.location + ' ' + self.type

    def to_dict(self):
        return functions.inbound_to_dict(self)

    def clean(self):
        try:
            if self.type == 'vless' and not self.tls:
                raise ValidationError("Tls section can not be empty when vless type is selected!")
        except Tls.DoesNotExist:
            raise ValidationError("Tls section can not be empty when vless type is selected!")


class Tls(models.Model):
    class Type(models.TextChoices):
        REALITY = 'reality', 'Reality'

    class TCPVersion(models.TextChoices):
        V1_0 = '1.0', 'Version 1.0'
        V1_1 = '1.1', 'Version 1.1'
        V1_2 = '1.2', 'Version 1.2'
        V1_3 = '1.3', 'Version 1.3'

    class uTLS(models.TextChoices):
        CHROME = 'chorme', 'Chrome'
        EDGE = 'edge', 'Edge'
        FIREFOX = 'firefox', 'Fire Fox'
        SAFARI = 'safari', 'Safari'
        QQ = 'qq' , 'QQ'
        IOS = 'ios', 'IOS'
        ANDROID = 'android', 'Android'
        RANDOM = 'random', 'Random'
        RANDOMIZED = 'randomized', 'Randomized'

    inbound = models.OneToOneField(Inbound, models.CASCADE, related_name='tls')
    type = models.CharField(max_length=8, choices=Type.choices)
    server_name = models.CharField(max_length=164)
    min_version = models.CharField(max_length=64, choices=TCPVersion.choices, null=True, blank=True)
    max_version = models.CharField(max_length=64, choices=TCPVersion.choices, null=True, blank=True)
    certificate = models.TextField(null=True, blank=True)
    certificate_path = models.CharField(max_length=64, null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    key_path = models.CharField(max_length=64, null=True, blank=True)
    utls = models.CharField(max_length=10, choices=uTLS.choices, null=True, blank=True)
    handshake_server = models.CharField(max_length=64)
    handshake_port = models.IntegerField(unique=True)
    private_key = models.CharField(max_length=64)
    public_key = models.CharField(max_length=64)
    short_id = models.CharField(max_length=64)

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=~models.Q(certificate__isnull=False, certificate_path__isnull=False) & ~models.Q(key__isnull=False, key_path__isnull=False),
                name="validate_key_and_certificate"),
        )


class InboundUser(models.Model):
    class Flow(models.TextChoices):
        XRV = 'xtls-rprx-vision', 'xtls-rprx-vision'

    inbound = models.ForeignKey(Inbound, models.CASCADE, 'users')
    uuid = models.CharField(max_length=64)
    flow = models.CharField(max_length=16, choices=Flow.choices, null=True, blank=True)


class TrafficUsage(models.Model):
    user = models.OneToOneField(InboundUser, models.CASCADE, related_name='traffic_usage')
    upload = models.BigIntegerField()
    download = models.BigIntegerField()
