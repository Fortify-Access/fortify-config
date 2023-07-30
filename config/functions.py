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
        {'inbounds': inbound_models.Inbound.objects.all(), 'server': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_mappings.conf', 'w') as config:
        config.write(nginx_mappings)

    nginx_upstreams = render_to_string(
        'nginx/upstreams_template.conf',
        {'inbounds': inbound_models.Inbound.objects.all(), 'server': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_upstreams.conf', 'w') as config:
        config.write(nginx_upstreams)

    subprocess.run(['nginx', '-s', 'reload'])

def create_a_dns_record(ip: str, cf):
    payload = {
        "content": ip, "name": f"{cf.original_domain}",
        "proxied": False, "type": "A",
        "comment": f"Record for {ip}", "ttl": 3600
    }
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {cf.token}" }

    response = requests.request("POST",
        f'https://api.cloudflare.com/client/v4/zones/{cf.zone_id}/dns_records',
        json=payload, headers=headers)
    response = response.json()

    if response['success']:
        return response['result']['id'], None

    return None, '\n'.join([f"CloudFlare Error: {error['code']} - {error['message']}" for error in response['errors']])
