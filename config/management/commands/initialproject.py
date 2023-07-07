from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initial Fortify Access Project'

    def add_arguments(self, parser):
        parser.add_argument('ip', type=str, help='Current server ip address')

    def handle(self, *args, **options):
        from config.models import Server
        Server.objects.create(host=options['ip'], is_local_server=True)
