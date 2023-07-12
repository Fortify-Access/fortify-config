from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initial Fortify Access Project'

    def add_arguments(self, parser):
        parser.add_argument('--ip', type=str, help='Current server ip address')
        parser.add_argument('-cz', '--cloudflare-zoneid', type=str, help='Cloudflare ZoneID')
        parser.add_argument('-ct', '--cloudflare-token', type=str, help='Cloudflare authentication token')
        parser.add_argument('-d', '--domain', type=str, help='The parent domain that will be set for inbounds')
        parser.add_argument('-p', '--port', type=int, help='Incoming server port')

    def handle(self, *args, **options):
        from config.models import Server, CloudFlareDNS

        if Server.objects.filter(is_local_server=True).exists():
            self.stdout.write(self.style.ERROR("This project already initialized!"))
            return

        if options.get('cloudflare_zoneid', None):
            if options.get('cloudflare_token', None) and options.get('domain', None) and options.get('port', None):
                server = Server.objects.create(host=options['ip'], is_local_server=True, incoming_port=options['port'])
                CloudFlareDNS.objects.create(
                    server=server, zone_id=options['cloudflare_zoneid'],
                    token=options['cloudflare_token'], original_domain=options['domain']
                )
                return
            self.stdout.write(self.style.ERROR('All --cloudflare-token, --domain and --port should be passed!'))
            return

        Server.objects.create(host=options['ip'], is_local_server=True)

        self.stdout.write(self.style.SUCCESS('Project successfully initialized.'))
