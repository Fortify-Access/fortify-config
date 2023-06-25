from django.apps import AppConfig


class InboundsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inbounds'

    def ready(self):
        import inbounds.signals
