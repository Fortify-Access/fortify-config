import requests
from inbounds import models as inbound_models
from config import models as config_models
from core.celery import app

@app.task(name='inbounds_updater')
def inbounds_updater():
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
