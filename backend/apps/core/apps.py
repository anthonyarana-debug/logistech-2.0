from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Infrastructure"

    def ready(self):
        from . import checks  # noqa: F401
