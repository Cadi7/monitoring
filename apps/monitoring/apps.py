from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    name = 'apps.monitoring'

    def ready(self):
        import apps.monitoring.signals
