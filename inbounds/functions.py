import subprocess
from django.conf import settings

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

def inbound_to_dict(inbound):
    users = [{'uuid': user.uuid, 'flow': user.flow} for user in inbound.users.all()]
    return {
        "type": inbound.type,
        "tag": inbound.tag,
        "listen": inbound.listen,
        "listen_port": inbound.listen_port,
        "sniff": inbound.sniff,
        "sniff_override_destination": inbound.sniff_override_destination,
        "domain_strategy": inbound.domain_strategy,
        "users": users,
        "tls": {} if inbound.type not in ['vless'] else tls_to_dict(inbound.tls),
    }
