# baseball/settings/prod.py
from .base import *

ALLOWED_HOSTS = [
    'totheballpark.info',
    'www.totheballpark.info',
]

# 1) HTTPS 강제
SECURE_SSL_REDIRECT = True

# 2) HSTS (안정화 후 1년으로 올리세요)
SECURE_HSTS_SECONDS = 86400
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False

# 3) 보안 쿠키
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_COOKIE_HTTPONLY = True

# 4) 프록시 뒤 HTTPS 인지
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 5) CSRF 신뢰 출처 — https만
CSRF_TRUSTED_ORIGINS = [
    'https://totheballpark.info',
    'https://www.totheballpark.info',
    'https://totheballpark.info:8443',
    'https://www.totheballpark.info:8443',
]

WHITENOISE_MANIFEST_STRICT = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config('DB_NAME'),
        "USER": config('DB_USER'),
        "PASSWORD": config('DB_PASSWORD'),
        "HOST": config('DB_HOST'),
        "PORT": config('DB_PORT'),
        "OPTIONS": {"sslmode": "require"},
    }
}