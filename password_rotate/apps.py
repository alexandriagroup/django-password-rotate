from django.apps import AppConfig


class PasswordRotateConfig(AppConfig):
    name = 'password_rotate'

    def ready(self):
        from . import signals
        signals.register_signals()
