import requests
from django.db.models import Q, F
from celery import shared_task
from datetime import datetime
import pytz
from inbounds import models as inbound_models
from config import models as config_models

@shared_task(name='inbounds_updater')
def inbounds_updater():
    for server in config_models.Server.objects.filter(subservers__isnull=False):
        try:
            subserver = server.subservers.first()
            headers = {'Authorization': f'Bearer {subserver.auth_key}'}
            response = requests.get(f"http://{subserver.host}:{subserver.api_port}/inbound/get_last_updates", headers=headers)
            response_json = response.json()

            updated_traffics = []
            if response_json['success']:
                for inbound_json in response_json['inbounds']:
                    inbound = inbound_models.Inbound.objects.get(tag=inbound_json['tag'])
                    inbound.traffic.upload = inbound_json['upload']
                    inbound.traffic.download = inbound_json['download']
                    inbound.traffic.traffic_usage = inbound_json['traffic_usage']
                    updated_traffics.append(inbound.traffic)

                    for client_ip in inbound_json['online_clients']:
                        created, client = inbound_models.ConnectionLog.objects.update_or_create(
                            inbound__tag=inbound_json['tag'], ip=client_ip,
                            defaults={'inbound': inbound, 'ip': client_ip, 'is_online': True})
                    inbound_models.ConnectionLog.objects.filter(Q(inbound__tag=inbound_json['tag']) & ~Q(ip__in=inbound_json['online_clients'])).update(is_online=False)

                    if inbound.ip_limitation or inbound.ip_limitation != 0:
                        if inbound.connections.filter(is_online=True).count() > inbound.ip_limitation:
                            inbound.status = 0
                            inbound.save()
                            inbound.push(created=False)

                inbound_models.Traffic.objects.bulk_update(updated_traffics, fields=('upload', 'download', 'traffic_usage'))
                continue
            error_msg = response_json['error']

        except Exception as e:
            error_msg = str(e)

        config_models.Log.objects.create(server=server, type=config_models.Log.Type.ERROR, log_message=error_msg)
        server.status = 0
        server.save()


@shared_task(name='expirations_checker')
def expirations_checker():
    expired = inbound_models.Inbound.objects.filter(
        status=inbound_models.Inbound.Status.ENABLED, expiration_date__lte=datetime.now(pytz.timezone('Asia/Tehran'))
    )
    expired.update(status=inbound_models.Inbound.Status.EXPIRED)
    for expired_inbound in expired.iterator():
        expired_inbound.push(False)

    depreted = inbound_models.Inbound.objects.filter(
        status=inbound_models.Inbound.Status.ENABLED, traffic__traffic_usage__gte=F('traffic__allowed_traffic')
    )
    depreted.update(status=inbound_models.Inbound.Status.DEPRETED)
    for depreted_inbound in depreted.iterator():
        depreted.push(False)


# @shared_task
# def push_to_server(inbound, server, action):
#     try:
#         headers = {'Authorization': f'Bearer {server.auth_key}'}
#         if action in ['created', 'modified']:
#             url = f"http://{server.host}:{server.api_port}/inbound/{'create' if action == 'created' else 'update?tag=' + instance.tag}"
#             print(functions.inbound_to_json(inbound))
#             response = requests.post(url, headers=headers, data=functions.inbound_to_json(inbound))
#         else:
#             url = f"http://{server.host}:{server.api_port}/inbound/delete?tag={inbound.tag}"
#             response = requests.post(url, headers=headers)
# 
#         if response.json()['success']:
#             return
#         error_msg = response.json()['error']
# 
#     except Exception as e:
#         error_msg = str(e)
# 
#     config_models.Log.objects.create(inbound=inbound, type=config_models.Log.Type.ERROR, log_message=error_msg)
#     inbound.status = 4
#     inbound.save()
#     return
