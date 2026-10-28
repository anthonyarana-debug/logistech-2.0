from collections.abc import Mapping
from datetime import UTC, datetime

from django.conf import settings
from django.db import transaction
from django.utils.crypto import salted_hmac
from rest_framework.throttling import SimpleRateThrottle


class AuthThrottle(SimpleRateThrottle):
    def allow_request(self, request, view):
        if not settings.USE_DATABASE_THROTTLE:
            return super().allow_request(request, view)
        if self.rate is None:
            return True
        cache_key = self.get_cache_key(request, view)
        if cache_key is None:
            return True
        key = salted_hmac("database-throttle", cache_key, algorithm="sha256").hexdigest()
        from apps.core.models import ThrottleWindow

        # The unique key arbitrates concurrent first inserts; the row lock then
        # serializes the read/prune/append across every process and connection.
        # Database errors deliberately propagate (the API returns its generic 500).
        with transaction.atomic():
            window, _ = ThrottleWindow.objects.select_for_update().get_or_create(
                key=key,
                defaults={"expires_at": datetime.fromtimestamp(self.timer(), tz=UTC)},
            )
            self.now = self.timer()
            self.history = [stamp for stamp in window.history if stamp > self.now - self.duration]
            if len(self.history) >= self.num_requests:
                return self.throttle_failure()
            self.history.insert(0, self.now)
            window.history = self.history
            window.expires_at = datetime.fromtimestamp(self.now + self.duration, tz=UTC)
            window.save(update_fields=["history", "expires_at"])
        return True

    def parse_rate(self, rate):
        # DRF no interpreta ventanas de varios minutos (por ejemplo 15min).
        count, period = rate.split("/")
        if period.endswith("min"):
            return int(count), 60 * int(period[:-3] or "1")
        return super().parse_rate(rate)

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class LoginIPThrottle(AuthThrottle):
    scope = "login_ip"


class LoginIdentityThrottle(AuthThrottle):
    scope = "login_identity"

    def get_cache_key(self, request, view):
        data = request.data if isinstance(request.data, Mapping) else {}
        email = str(data.get("email", ""))[:254].strip().lower()
        digest = salted_hmac("auth-throttle", email).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": digest}


class RegistrationThrottle(AuthThrottle):
    scope = "register"


class RefreshThrottle(AuthThrottle):
    scope = "refresh"


class LogoutThrottle(AuthThrottle):
    scope = "logout"


class CsrfThrottle(AuthThrottle):
    scope = "csrf"
