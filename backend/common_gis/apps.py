from django.apps import AppConfig


class CommonGisConfig(AppConfig):
    name = 'common_gis'

    def ready(self):
            import common_gis.signals