from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import json
import os

from . import models
from . import functions
from config import functions as config_funcs


@receiver(post_save, sender=models.Inbound)
def commit_inbound_to_singbox(sender, instance, created, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        config_dict = json.loads(config.read())
        if created:
            config_dict['inbounds'].append(instance.to_dict())
        else:
            for index, inbound in enumerate(config_dict['inbounds']):
                if inbound['tag'] == instance.tag:
                    config_dict['inbounds'][index] = instance.to_dict()

        config_dict = json.dumps(config_dict, indent=2)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
        if hasattr(instance.server, 'dns'):
            functions.generate_subdomain_in_cf(instance.tag, instance.server.dns)

        config_funcs.restart_singbox()
        config_funcs.reload_nginx()


@receiver(post_save, sender=models.InboundUser)
def commit_inbound_user_to_singbox(sender, instance, created, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        config_dict = json.loads(config.read())
        for index, inbound in enumerate(config_dict['inbounds']):
            if inbound['tag'] == instance.inbound.tag:
                if created:
                    config_dict['inbounds'][index]['users'].append(instance.to_dict())
                else:
                    config_dict['inbounds'][index]['users'][instance.uuid] = instance.to_dict()
                    os.remove(settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')

            functions.generate_qr_code(instance.connection_code, settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')

        config_dict = json.dumps(config_dict, indent=2)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
        config_funcs.restart_singbox()
        config_funcs.reload_nginx()


@receiver(post_delete, sender=models.Inbound)
def delete_inbound_from_singbox(sender, instance, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        config_dict = json.loads(config.read())
        for index, inbound in enumerate(config_dict['inbounds']):
            if inbound['tag'] == instance.tag:
                config_dict['inbounds'].pop(index)

        config_dict = json.dumps(config_dict, indent=2)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
        config_funcs.restart_singbox()
        config_funcs.reload_nginx()


@receiver(post_delete, sender=models.InboundUser)
def delete_inbound_user_from_singbox(sender, instance, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        config_dict = json.loads(config.read())
        for index, inbound in enumerate(config_dict['inbounds']):
            if inbound['tag'] == instance.inbound.tag:
                config_dict['inbounds'][index]['users'][instance.uuid] = instance.to_dict()
                os.remove(settings.MEDIA_ROOT / 'qr_codes' / f'{instance.id}.png')

        config_dict = json.dumps(config_dict, indent=2)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
        config_funcs.restart_singbox()
        config_funcs.reload_nginx()
