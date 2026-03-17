from .base import *
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config("CSRF_TRUSTED_ORIGINS").split(",")
    if origin.strip()
]

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Render roda instância única — LocMemCache é suficiente para rate limiting.
# Migrar para Redis se escalar para múltiplas instâncias.
SILENCED_SYSTEM_CHECKS = ["django_ratelimit.E003", "django_ratelimit.W001"]