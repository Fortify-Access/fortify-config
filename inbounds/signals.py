from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests
import json
from . import models
from . import functions
from config.models import Log


@receiver(post_save, sender=models.Inbound)
def push_inbound_to_subservers(sender, instance, created, **kwargs):
    def push(server, created: bool):
        headers = {'Authorization': f'Bearer {server.auth_key}'}
        url = f"http://{server.host}:{server.api_port}/inbound/{'create' if created else 'update?tag=' + instance.tag}"
        response = requests.post(url, headers=headers, data=json.dumps(functions.inbound_to_json(instance)))
        print(functions.inbound_to_json(instance))

        if not response.json()['success']:
            Log.objects.create(inbound=instance, type=Log.Type.ERROR, log_message=response.json()['error'])
            instance.status = 4
            instance.save()

    if created:
        if instance.server.subservers.exists():
            for subserver in instance.server.subservers.all():
                push(subserver, True)
            return
        push(instance.server, True)
    else:
        if instance.server.subservers.exists():
            for subserver in instance.server.subservers.all():
                push(subserver, False)
            return
        push(instance.server, False)


@receiver(post_delete, sender=models.Inbound)
def delete_inbound_from_singbox(sender, instance, **kwargs):
    def push(server):
        headers = {'Authorization': f'Bearer {server.auth_key}'}
        url = f"http://{server.host}:{server.api_port}/inbound/delete?tag={instance.tag}"
        response = requests.post(url, headers=headers)

        if not response.json()['success']:
            Log.objects.create(inbound=instance, type=Log.Type.ERROR, log_message=response.json()['error'])
            instance.status = 4
            instance.save()

        if instance.server.subservers.exists():
            for subserver in instance.server.subservers.all():
                push(subserver, True)
            return
        push(instance.server, True)


# @receiver(post_save, sender=models.InboundUser)
# def commit_inbound_user_to_singbox(sender, instance, created, **kwargs):
#     with open(settings.SING_BOX_CONF_PATH, 'r') as config:
#         config_dict = json.loads(config.read())
#         for index, inbound in enumerate(config_dict['inbounds']):
#             if inbound['tag'] == instance.inbound.tag:
#                 if created:
#                     config_dict['inbounds'][index]['users'].append(instance.to_dict())
#                 else:
#                     config_dict['inbounds'][index]['users'][instance.uuid] = instance.to_dict()
#                     os.remove(settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')
# 
#             functions.generate_qr_code(instance.connection_code, settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')
# 
#         config_dict = json.dumps(config_dict, indent=2)
#         open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
#         config_funcs.restart_singbox()
#         config_funcs.reload_nginx()


# @receiver(post_delete, sender=models.InboundUser)
# def delete_inbound_user_from_singbox(sender, instance, **kwargs):
#     with open(settings.SING_BOX_CONF_PATH, 'r') as config:
#         config_dict = json.loads(config.read())
#         for index, inbound in enumerate(config_dict['inbounds']):
#             if inbound['tag'] == instance.inbound.tag:
#                 config_dict['inbounds'][index]['users'][instance.uuid] = instance.to_dict()
#                 os.remove(settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')
# 
#         config_dict = json.dumps(config_dict, indent=2)
#         open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
#         config_funcs.restart_singbox()
#         config_funcs.reload_nginx()
