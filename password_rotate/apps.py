from django.apps import AppConfig


class PasswordRotateConfig(AppConfig):
    name = 'password_rotate'
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals
        signals.register_signals()
