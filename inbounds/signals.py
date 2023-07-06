from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json
import os

from . import models
from . import functions


@receiver(post_save, sender=models.Inbound)
def commit_inbound_to_singbox(sender, instance, created, **kwargs):
    with open(settings.SING_BOX_CONF_PATH, 'r') as config:
        if created:
            config_dict = json.loads(config.read())
            config_dict['inbounds'].append(instance.to_dict())
        else:
            for index, inbound in enumerate(config_dict['inbounds']):
                if inbound['tag'] == instance.tag:
                    config_dict['inbounds'][index] = instance.to_dict()

        config_dict = json.dumps(config_dict, indent=2)
        open(settings.SING_BOX_CONF_PATH, 'w').write(config_dict)
    print("Gooooooooooooh")


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
