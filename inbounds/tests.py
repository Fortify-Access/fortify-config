from django.test import TestCase
from django.db.models import F, Q
from . import models
from config import models as config_models

# Create your tests here.
class InbuondsUpdaterTest(TestCase):
    def setUp(self):
        for i in range(100):
            parent = config_models.Server.objects.create(host=str(i), location="Global", redis_port=i)

            for k in range(4):
                config_models.Server.objects.create(host=str(k), location="Local", api_port=k, parent_server=parent, auth_key=str(k))

            for x in range(100):
                inbound = models.Inbound.objects.create(
                    server=parent, tag=str(i), listen_port=x, tcp_fast_open=False,
                    udp_fragment = False, sniff = False, sniff_override_destination = False,
                    proxy_protocol = False, proxy_protocol_accept_no_header = False,
                )
                models.Traffic.objects.create(inbound=inbound, traffic_usage=2, allowed_traffic=1)

    def test_inbounds_updater(self):
        for server in config_models.Server.objects.filter(subservers__isnull=False):
            try:
                subserver = server.subservers.first()
                response_json = {'success': True}

                updated_traffics = []
                if response_json['success']:
                    inbounds_tags = [inbound_dict['tag'] for inbound_dict in response_json["inbounds"]]
                    models.Traffic.objects.filter(inbound__tag__in=inbounds_tags).update(
                        upload=response_json['inbounds'][F('inbound__tag')]['upload'],
                        download=response_json['inbounds'][F('inbound__tag')]['download'],
                        traffic_usage=response_json['inbounds'][F('inbound__tag')]['traffic_usage'],
                    )
                    for inbound in models.Inbound.all():
                        # inbound.traffic.upload = 1
                        # inbound.traffic.download = 2
                        # inbound.traffic.traffic_usage = 3
                        # updated_traffics.append(inbound.traffic)

                        for client_ip in ['127.0.0.1', '127.0.0.2']:
                            created, client = models.ConnectionLog.objects.update_or_create(
                                inbound=inbound, ip=client_ip,
                                defaults={'inbound': inbound, 'ip': client_ip, 'is_online': True})
                        models.ConnectionLog.objects.filter(Q(inbound=inbound) & ~Q(ip__in=['127.0.0.1', '127.0.0.2'])).update(is_online=False)

                        if inbound.ip_limitation or inbound.ip_limitation != 0:
                            if inbound.connections.filter(is_online=True).count() > inbound.ip_limitation:
                                inbound.status = 0
                                inbound.save()
                                inbound.push(created=False)

                    # models.Traffic.objects.bulk_update(updated_traffics, fields=('upload', 'download', 'traffic_usage'))
                    continue
                error_msg = response_json['error']

            except Exception as e:
                error_msg = str(e)

            config_models.Log.objects.create(server=server, type=config_models.Log.Type.ERROR, log_message=error_msg)
            server.status = 0
            server.save()


class InboundsExpirationCheckerTest(TestCase):
    def setUp(self):
        server = config_models.Server.objects.create(host="0.0.0.0", location="Global", redis_port=6379)
        for i in range(100):
            inbound = models.Inbound.objects.create(
                server=server, tag=str(i), listen_port=i, tcp_fast_open=False,
                udp_fragment = False, sniff = False, sniff_override_destination = False,
                proxy_protocol = False, proxy_protocol_accept_no_header = False,
            )
            models.Traffic.objects.create(inbound=inbound, traffic_usage=2, allowed_traffic=1)

    def test_inbounds_expirations_via_save_method(self):
        for inbound in models.Inbound.objects.filter(status=models.Inbound.Status.ENABLED,
                                                             traffic__traffic_usage__gte=F('traffic__allowed_traffic')).iterator():
            inbound.status = models.Inbound.Status.DEPRETED
            inbound.save()

    def test_inbounds_expirations_via_update_method(self):
        models.Inbound.objects.filter(
            status=models.Inbound.Status.ENABLED, traffic__traffic_usage__gte=F('traffic__allowed_traffic')
        ).update(status=models.Inbound.Status.DEPRETED)
