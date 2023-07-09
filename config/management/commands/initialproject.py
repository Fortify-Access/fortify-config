from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initial Fortify Access Project'

    def add_arguments(self, parser):
        parser.add_argument('--ip', type=str, help='Current server ip address')
        parser.add_argument('-cz', '--cloudflare-zoneid', type=str, help='Cloudflare ZoneID')
        parser.add_argument('-ct', '--cloudflare-token', type=str, help='Cloudflare authentication token')
        parser.add_argument('-d', '--domain', type=str, help='The parent domain that will be set for inbounds')

    def handle(self, *args, **options):
        from config.models import Server, CloudFlareDNS

        if options.get('cloudflare-zoneid', None):
            if options.get('cloudflare-token', None) and options.get('domain', None):
                server = Server.objects.create(host=options['ip'], is_local_server=True)
                CloudFlareDNS.objects.create(
                    server=server, zone_id=options['cloudflare-zoneid'],
                    token=options['cloudflare-token'], original_domain=options['domain']
                )
                return
            self.stdout.write(self.style.ERROR('Both --cloudflare-token and --domain should be passed!'))
            return

        Server.objects.create(host=options['ip'], is_local_server=True)

        self.stdout.write(self.style.SUCCESS('Project successfully initialized.'))
