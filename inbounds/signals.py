from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import json
from . import models


@receiver(post_save, sender=models.Inbound)
def commit_inbound_to_singbox_pre_save(sender, instance, created, **kwargs):
    if created:
        with open('core/config.json', 'r') as config:
            config_dict = json.loads(config.read())
            config_dict['inbounds'].append(instance.to_dict())
            config_dict = json.dumps(config_dict)
            open('core/config.json', 'w').write(config_dict)


# @receiver(pre_delete, sender=models.Inbound)
# def remove_inbound_from_singbox_pre_save(sender, instance, **kwargs):
#     pass
