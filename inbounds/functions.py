import subprocess
from django.conf import settings
from django.forms.models import model_to_dict
import qrcode
import requests

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

def inbound_to_json(inbound):
    return {
        "inbound": model_to_dict(inbound, exclude=('server', 'status')) | {'traffic_limitation': inbound.traffic.allowed_traffic},
        "users": [model_to_dict(user, fields=('name', 'uuid', 'flow')) for user in inbound.users],
        "tls": None if not hasattr(inbound, 'tls') else model_to_dict(inbound.tls, fields=(
            'type', 'server_name', 'handshake_server', 'handshake_port', 'private_key', 'short_id')),
        # "transport": None if not hasattr(inbound, 'transport') else transport_to_dict(inbound.transport)
    }

def generate_qr_code(data: str, path):
    print(type(path))
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    image = qr.make_image(fill_color='#007bff', back_color='#f4f5f7')
    image.save(path)
    return path

def generate_subdomain_in_cf(subdomain: str, cf):
    payload = {
        "content": cf.original_domain, "name": f"{subdomain}.{cf.original_domain}",
        "proxied": False, "type": "CNAME",
        "comment": f"Inbound subdomain for {cf.server.host}-{subdomain}", "ttl": 3600
    }
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {cf.token}" }

    response = requests.request("POST",
        f'https://api.cloudflare.com/client/v4/zones/{cf.zone_id}/dns_records',
        json=payload, headers=headers)
    response = response.json()

    if response['success']:
        return response['result']['id'], None

    return None, '\n'.join([f"CloudFlare Error: {error['code']} - {error['message']}" for error in response['errors']])

def delete_subdomain_from_cf(subdomain_id: str, cf):
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {cf.token}" }

    response = requests.request("DELETE",
        f'https://api.cloudflare.com/client/v4/zones/{cf.zone_id}/dns_records/{subdomain_id}',
        headers=headers)
    response = response.json()

    if response['success']:
        return True, None

    return False, '\n'.join([f"CloudFlare Error: {error['code']} - {error['message']}" for error in response['errors']])
