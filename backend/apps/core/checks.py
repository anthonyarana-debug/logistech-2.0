from django.apps import apps
from django.conf import settings
from django.core.checks import Error, Tags, register

from apps.core.messages import message


@register(Tags.models)
def prevent_default_user_migration(app_configs, **kwargs):
    """Impide habilitar auth con el usuario desechable del proyecto base."""
    if apps.is_installed("django.contrib.auth") and settings.AUTH_USER_MODEL == "auth.User":
        return [
            Error(
                message("do_not_enable_authentication_with_auth_user"),
                hint=message(
                    "create_accounts_user_and_its_0001_initial_before_migrating_auth_admin"
                ),
                id="logistech.E001",
            )
        ]
    return []


@register(Tags.security, deploy=True)
def warn_load_test_mode(app_configs, **kwargs):
    """Recuerda que los rate limits están desactivados durante una prueba de carga."""
    from django.core.checks import Warning

    if getattr(settings, "LOAD_TEST_MODE", False):
        return [
            Warning(
                "LOAD_TEST_MODE=true: rate limits are disabled.",
                hint="Set LOAD_TEST_MODE=false and recreate the backend after the load test.",
                id="logistech.W010",
            )
        ]
    return []
