from collections.abc import Mapping

from django.utils.crypto import salted_hmac
from rest_framework.throttling import SimpleRateThrottle


class AuthThrottle(SimpleRateThrottle):
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
