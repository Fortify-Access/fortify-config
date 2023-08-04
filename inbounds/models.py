from django.db import models
from django.core.exceptions import ValidationError
import requests
import json
from config import models as config_models
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

    class Status(models.IntegerChoices):
        DISABLED = 0, 'Disabled'
        ENABLED = 1, 'Enabled'
        EXPIRED = 2, 'Expired'
        DEPRETED = 3, 'Depreted'
        ERROR = 4, 'Error'

    server = models.ForeignKey('config.Server', models.CASCADE, 'inbounds')
    type = models.CharField(max_length=5, choices=Type.choices)
    tag = models.CharField(max_length=8)
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


    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.ENABLED)
    expiration_date = models.DateTimeField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    ip_limitation = models.PositiveSmallIntegerField(default=2, null=True, blank=True)

    def __str__(self):
        return self.server.location + ' ' + self.type

    def to_dict(self):
        return functions.inbound_to_dict(self)

    @property
    def online_clients_count(self):
        return self.connections.filter(is_online=True).count()

    def _push_request(self, server, action):
        try:
            headers = {'Authorization': f'Bearer {server.auth_key}'}
            if action in ['created', 'modified']:
                url = f"http://{server.host}:{server.api_port}/inbound/{'create' if action == 'created' else 'update?tag=' + instance.tag}"
                print(functions.inbound_to_json(self))
                response = requests.post(url, headers=headers, data=json.dumps(functions.inbound_to_json(self)))
            else:
                url = f"http://{server.host}:{server.api_port}/inbound/delete?tag={self.tag}"
                response = requests.post(url, headers=headers)

            if response.json()['success']:
                return
            error_msg = response.json()['error']

        except Exception as e:
            raise e
            error_msg = str(e)

        config_models.Log.objects.create(inbound=self, type=config_models.Log.Type.ERROR, log_message=error_msg)
        self.status = 4
        self.save()
        return

    def push(self, created=True, *args, **kwargs):
        super(Inbound, self).save(*args, **kwargs)
        print(created)
        if self.server.subservers.exists():
            for subserver in self.server.subservers.all():
                print(subserver.host)
                self._push_request(subserver, 'created' if created else 'modified')
            return
        self._push_request(self.server, created)

    def delete(self):
        super().delete()
        if self.server.subservers.exists():
            for subserver in self.server.subservers.all():
                self._push_request(subserver, 'deleted')
            return
        self._push_request(self.server, 'deleted')

    def clean(self):
        super(Inbound, self).clean()
        if Inbound.objects.filter(server=self.server, listen_port=self.listen_port).exists():
            return ValidationError({'listen_port': 'This port is already exists among the inbounds of their server with your selected server. Please choose another port'})


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
    server_name = models.CharField(max_length=164, default='discord.com')
    # min_version = models.CharField(max_length=64, choices=TCPVersion.choices, null=True, blank=True)
    # max_version = models.CharField(max_length=64, choices=TCPVersion.choices, null=True, blank=True)
    # certificate = models.TextField(null=True, blank=True)
    # certificate_path = models.CharField(max_length=64, null=True, blank=True)
    # key = models.TextField(null=True, blank=True)
    # key_path = models.CharField(max_length=64, null=True, blank=True)
    utls = models.CharField(max_length=10, choices=uTLS.choices, null=True, blank=True)
    handshake_server = models.CharField(max_length=64, default='discord.com')
    handshake_port = models.IntegerField(default=443)
    private_key = models.CharField(max_length=64, unique=True)
    public_key = models.CharField(max_length=64, unique=True)
    short_id = models.CharField(max_length=64, unique=True)

    # class Meta:
    #     constraints = (
    #         models.CheckConstraint(
    #             check=~models.Q(certificate__isnull=False, certificate_path__isnull=False) & ~models.Q(key__isnull=False, key_path__isnull=False),
    #             name="validate_key_and_certificate"),
    #     )


class Transport(models.Model):
    class Type(models.TextChoices):
        HTTP = 'http', 'Http'
        WS = 'ws', 'WebSocket'

    class Method(models.TextChoices):
        GET = 'GET', 'GET'

    inbound = models.OneToOneField(Inbound, models.CASCADE, related_name='transport')
    hosts = models.CharField(max_length=364, null=True, blank=True, help_text='Use comma to separate hosts.')
    type = models.CharField(max_length=4, choices=Type.choices)
    path = models.CharField(max_length=64, default='/')
    method = models.CharField(max_length=3, choices=Method.choices, null=True, blank=True)

    def to_dict(self):
        return functions.transport_to_dict(self)

    class Meta:
        constraints = (
            models.CheckConstraint(
                check=~models.Q(type='ws', method__isnull=False) & ~models.Q(type='http', hosts__isnull=True),
                name="vlidate_transport_type"
            ),
        )


class InboundUser(models.Model):
    class Flow(models.TextChoices):
        XRV = 'xtls-rprx-vision', 'xtls-rprx-vision'

    inbound = models.OneToOneField(Inbound, models.CASCADE, related_name='user')
    name = models.CharField(max_length=10, null=True, blank=True)
    uuid = models.CharField(max_length=64, unique=True)
    flow = models.CharField(max_length=16, choices=Flow.choices, null=True, blank=True)

    def to_dict(self):
        return functions.inbound_user_to_dict(self)

    @property
    def connection_code(self):
        code_pattern = f"{self.inbound.type}://{self.uuid}@\{self.inbound.server.server_domain or self.server.host}:\{self.inbound.listen_port}?encryption=none&flow={self.flow}&" 

        if self.inbound.type == 'vmess':
            return code_pattern + f"security=none&type=http&headerType=none#{self.inbound.tag}"
        if hasattr(self.inbound, 'tls'):
            if self.inbound.tls.type == 'reality':
                return code_pattern + f"security=reality&sni={self.inbound.tls.server_name}&fp={self.inbound.tls.utls}&pbk={self.inbound.tls.public_key}&sid={self.inbound.tls.short_id}&type=tcp&headerType=none#{self.inbound.tag}"

    @property
    def connection_qr_code(self):
        return f'qr_codes/{self.id}.png'


class Traffic(models.Model):
    inbound = models.OneToOneField(Inbound, models.CASCADE, related_name='traffic')
    allowed_traffic = models.BigIntegerField(null=True, blank=True, help_text='Giga Bytes')
    traffic_usage = models.BigIntegerField(default=0)
    download = models.BigIntegerField(default=0)
    upload = models.BigIntegerField(default=0)

    # class Meta:
    #     constraints = (
    #         models.CheckConstraint(
    #             check=~models.Q(inbound__isnull=True, user__isnull=True) & ~models.Q(inbound__isnull=False, user__isnull=False),
    #             name='validate_traffic_parent_model'
    #         ),
    #     )

class ConnectionLog(models.Model):
    inbound = models.ForeignKey(Inbound, models.CASCADE, 'connections')
    ip = models.CharField(max_length=12)
    is_online = models.BooleanField(default=True)
