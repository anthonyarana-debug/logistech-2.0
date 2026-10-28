from django.db import models


class ThrottleWindow(models.Model):
    """Shared, short-lived quotas; keys never contain client IPs or identities."""

    key = models.CharField(max_length=64, primary_key=True)
    history = models.JSONField(default=list)
    expires_at = models.DateTimeField(db_index=True)
