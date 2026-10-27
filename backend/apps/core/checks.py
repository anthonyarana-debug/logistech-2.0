from django.apps import apps
from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.models)
def prevent_default_user_migration(app_configs, **kwargs):
    """Impide habilitar auth con el usuario desechable del proyecto base."""
    if apps.is_installed("django.contrib.auth") and settings.AUTH_USER_MODEL == "auth.User":
        return [
            Error(
                "No habilites autenticación con auth.User.",
                hint="Crea accounts.User y su 0001_initial antes de migrar auth/admin.",
                id="logistech.E001",
            )
        ]
    return []
