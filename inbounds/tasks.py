from celery import shared_task
import requests
from inbounds import models as inbound_models
from config import models as config_models

@shared_task
def update_inbounds():
    for server in config_models.Server.objects.filter(subserver__isnull=False):
        subserver = server.subservers.first()
        headers = {'Authorization': f'Bearer {subserver.auth_key}'}
        response = requests.get(f"{subserver.host}:{subserver.api_port}/inbound/get_last_updates", headers=headers)
        response_json = response.json()

        updated_traffics = []
        if response_json['success']:
            for inbound_json in response_json['inbounds']:
                traffic = inbound_models.Traffic.objects.get(inbound__tag=inbound_json['tag'])
                traffic.upload = inbound_json['upload']
                traffic.download = inbound_json['download']
                traffic.traffic_usage = inbound_json['traffic_usage']
                updated_traffics.append(traffic)

                for client_ip in inbound_json['online_clients']:
                    created, client = inbound_models.ConnectionLog.objects.update_or_create(
                        inbound__tag=inbound_json['tag'],
                        defaults={'ip': client_ip, 'is_online': True})

                inbound_models.ConnectionLog.objects.filter(inbound__tag=inbound_json['tag'], ip__notin=inbound_json['online_clients']).update(is_online=False)

            inbound_models.Traffic.objects.bulk_update(updated_traffics, fields=('upload', 'download', 'traffic_usage'))
