from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json

from . import models
from config import functions


@receiver(post_save, sender=models.Inbound)
def commit_inbound_to_singbox(sender, instance, created, **kwargs):
    if created:
        with open(settings.SING_BOX_CONF_PATH, 'r') as config:
            config_dict = json.loads(config.read())
            config_dict['inbounds'].append(instance.to_dict())
            config_dict = json.dumps(config_dict)
            open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
            functions.reload_singbox()
            functions.reload_nginx()


@receiver(post_save, sender=models.InboundUser)
def commit_inbound_user_to_singbox(sender, instance, created, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        config_dict = json.loads(config.read())
        for index, inbound in enumerate(config_dict['inbounds']):
            if inbound['unique_code'] == instance.inbound.unique_code:
                if created:
                    config_dict['inbounds'][index]['users'].append(instance.to_dict())
                else:
                    config_dict['inbounds'][index]['users'][instance.uuid] = instance.to_dict

        config_dict = json.dumps(config_dict)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
        functions.reload_singbox()
        functions.reload_nginx()
