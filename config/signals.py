import subprocess
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import models

# 
# @receiver(post_save, sender=models.Server)
# def run_redis_docker_container_for_server(sender, instance, created, **kwargs):
#     if created:
#         subprocess.check_output(['docker', 'run', '--name', instance.host, '-p', f'{instance.redis_port}:6379', '-d', 'redis'])
# 
# 
# @receiver(post_delete, sender=models.Server)
# def delete_redis_docker_container_of_server(sender, instance, **kwargs):
#     subprocess.check_output(['docker', 'rm', '-f', instance.host])
