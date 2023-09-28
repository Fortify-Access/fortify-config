from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initial Fortify Access Project'

    def add_arguments(self, parser):
        parser.add_argument('--ip', type=str, help='Current server ip address')

    def handle(self, *args, **options):
        from config.models import Server

        if Server.objects.filter(is_local_server=True).exists():
            self.stdout.write(self.style.ERROR("This project already initialized!"))
            return

        Server.objects.create(host=options['ip'], redis_port=5080, is_local_server=True)

        self.stdout.write(self.style.SUCCESS('Project successfully initialized.'))
