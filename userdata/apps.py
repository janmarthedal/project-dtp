from django.apps import AppConfig


class UserDataConfig(AppConfig):
    name = 'userdata'

    def ready(self):
        import userdata.signals
