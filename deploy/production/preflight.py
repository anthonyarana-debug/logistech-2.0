"""Validate resolved public deployment configuration; never read secret contents."""

import json
import re
import sys
from urllib.parse import urlsplit


def fail(message):
    print(f"Preflight rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


config = json.load(sys.stdin)
rehearsal = len(sys.argv) == 2 and sys.argv[1] == "true"
proxy = config["services"]["proxy"]
backend = config["services"]["backend"]
domain = proxy["environment"]["PUBLIC_DOMAIN"]
origin = backend["environment"]["CSRF_TRUSTED_ORIGINS"]
email = proxy["environment"]["ACME_EMAIL"]
source_ref = backend["image"].rsplit(":", 1)[-1]

if any(re.search(r"replace|reemplazar|placeholder", value, re.I) for value in (domain, origin, email, source_ref)):
    fail("replace every configuration placeholder before deployment")
if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", domain) or ".." in domain:
    fail("PUBLIC_DOMAIN must be one explicit hostname without scheme or port")
try:
    parsed = urlsplit(origin)
    port = parsed.port
except ValueError:
    fail("PUBLIC_ORIGIN is malformed")
if (
    parsed.scheme != "https"
    or parsed.hostname != domain
    or parsed.path
    or parsed.query
    or parsed.fragment
    or parsed.username
    or parsed.password
    or backend["environment"]["ALLOWED_HOSTS"] != domain
):
    fail("PUBLIC_ORIGIN and ALLOWED_HOSTS must match the single HTTPS public hostname")

if rehearsal:
    if domain != "localhost" or port != 8447:
        fail("rehearsal requires localhost and https://localhost:8447")
    published = {(p.get("host_ip"), p["published"]) for p in proxy.get("ports", [])}
    if published != {("127.0.0.1", "8087"), ("127.0.0.1", "8447")}:
        fail("rehearsal proxy ports must be loopback-only 8087/8447")
else:
    reserved = (".invalid", ".localhost", ".test", ".example")
    if domain == "localhost" or "." not in domain or domain.lower().endswith(reserved):
        fail("PUBLIC_DOMAIN must be a real public DNS hostname")
    if port not in (None, 443):
        fail("production PUBLIC_ORIGIN must use standard HTTPS port 443")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        fail("ACME_EMAIL must be a valid operator email address")
    email_domain = email.rsplit("@", 1)[-1].lower()
    if email_domain.endswith(reserved) or email_domain in {"example.com", "example.net", "example.org"}:
        fail("replace the sample ACME_EMAIL with a real operator email address")
    if not re.fullmatch(r"[0-9a-f]{40}", source_ref):
        fail("production SOURCE_REF must be the full immutable Git commit SHA")

print("Public configuration preflight passed (local rehearsal)." if rehearsal else "Public configuration preflight passed (production).")
