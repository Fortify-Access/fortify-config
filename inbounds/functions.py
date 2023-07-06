import subprocess
from django.conf import settings
import qrcode

def get_reality_keypair():
    key_pair = subprocess.check_output([settings.SING_BOX_PATH, "generate", "reality-keypair"]).decode('utf-8')
    private_key = key_pair.split('\n')[0].split(':')[-1].strip()
    public_key = key_pair.split('\n')[1].split(':')[-1].strip()

    return private_key, public_key

def get_uuid():
    return subprocess.check_output([settings.SING_BOX_PATH, "generate", "uuid"]).decode('utf-8')

def get_short_id():
    return subprocess.check_output([settings.SING_BOX_PATH, "generate", "rand", "--hex", "8"]).decode('utf-8')

def tls_to_dict(tls):
    tls_data = {
        "enabled": True,
        "server_name": tls.server_name,
    }

    if tls.type == 'reality':
        tls_data['reality'] = {
            "enabled": True,
            "handshake": {
                "server": tls.handshake_server,
                "server_port": tls.handshake_port,
            },
            "private_key": tls.private_key,
            "short_id": [tls.short_id],
        }
    return tls_data

def transport_to_dict(transport):
    transport_dict = {
        "type": transport.type,
        "path": transport.path,
    }

    if transport.type == 'http' and transport.method:
        transport_dict["method"] = transport.method
    if transport.type == 'http' and transport.hosts:
        transport_dict["host"] = [host for host in transport.hosts.split(',')]

    return transport_dict

def inbound_user_to_dict(inbound_user):
    return {'name': inbound_user.name, 'uuid': inbound_user.uuid, 'flow': inbound_user.flow}

def inbound_to_dict(inbound):
    return {
        "type": inbound.type,
        "tag": inbound.tag,
        "listen": inbound.listen,
        "listen_port": inbound.listen_port,
        "sniff": inbound.sniff,
        "sniff_override_destination": inbound.sniff_override_destination,
        "domain_strategy": inbound.domain_strategy,
        "users": [],
        "tls": None if not hasattr(inbound, 'tls') else tls_to_dict(inbound.tls),
        "transport": None if not hasattr(inbound, 'transport') else transport_to_dict(inbound.transport)
    }

def generate_qr_code(data: str, path):
    print(type(path))
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color='#007bff', back_color='#f4f5f7')
    image.save(path)
    return path
