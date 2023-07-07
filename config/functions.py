import subprocess
from django.template.loader import render_to_string

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
        'nginx_templates/mappings_template.conf',
        {'users': inbound_models.InboundUser.objects.all(), 'host': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_mappings.conf', 'w') as config:
        config.write(nginx_mappings)

    nginx_upstreams = render_to_string(
        'nginx_templates/upstreams_template.conf',
        {'users': inbound_models.InboundUser.objects.all(), 'host': models.Server.objects.get(is_local_server=True)})
    with open('services/nginx_upstreams.conf', 'w') as config:
        config.write(nginx_upstreams)

    subprocess.run(['nginx', '-s', 'reload'])
