from django.apps import AppConfig


class LdmsConfig(AppConfig):
    name = 'ldms'

    def ready(self):
        print ("I am ready")
        import ldms.signals