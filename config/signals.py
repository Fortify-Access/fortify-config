from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from . import functions


@receiver(post_save, sender=models.Server)
def initial_server(sender, instance, created, **kwargs):
    if hasattr(instance, 'dns') and created:
        original_domain_id, log_message = functions.create_aaaa_dns_record(instance.host, instance.dns)
        if not original_domain_id:
            instance.status = models.Server.Status.ERROR
            instance.save()
            models.Log.objects.create(server=instance, type=models.Log.Type.ERROR, log_message=log_message)
            return
        instance.dns.original_domain_id = original_domain_id
        instance.dns.save()

