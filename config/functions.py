import subprocess
from django.template.loader import render_to_string
import requests
from inbounds import models as inbound_models
from . import models


def restart_singbox():
    try:
        subprocess.check_output(["systemctl", "restart", "singbox.service"])
        return True
    except Exception as e:
        print(e)
        return False

def reload_nginx():
    nginx_mappings = render_to_string(
        'nginx/mappings_template.conf',
        {'users': inbound_models.InboundUser.objects.all(), 'host': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_mappings.conf', 'w') as config:
        config.write(nginx_mappings)

    nginx_upstreams = render_to_string(
        'nginx/upstreams_template.conf',
        {'users': inbound_models.InboundUser.objects.all(), 'host': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_upstreams.conf', 'w') as config:
        config.write(nginx_upstreams)

    subprocess.run(['nginx', '-s', 'reload'])

def create_aaaa_dns_record(ip: str, cf):
    payload = {
        "content": ip, "name": f"{cf.original_domain}",
        "proxied": False, "type": "AAAA",
        "comment": f"Record for {ip}", "ttl": 3600
    }
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {cf.token}" }

    response = requests.request("POST",
        f'https://api.cloudflare.com/client/v4/zones/{cf.zone_id}/dns_records',
        json=payload, headers=headers)
    response = response.json()

    if response['success']:
        return True, None

    return False, '\n'.join([f"{key} - {value}" for key, value in response['errors'].items()])
