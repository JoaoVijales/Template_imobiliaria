"""
Development settings for Imobiliária project.
Loads local .env file via django-environ.
"""

import environ

from .base import *  # noqa: F401, F403
from .base import BASE_DIR

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

env = environ.Env(
    DEBUG=(bool, True),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# Read the .env file from the project root (optional – won't fail if absent)
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-change-in-production")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Database – SQLite by default for local development
# ---------------------------------------------------------------------------

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

# ---------------------------------------------------------------------------
# Email – console backend for development
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Media & static overrides
# ---------------------------------------------------------------------------

MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "media"))
STATIC_ROOT = env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))

# ---------------------------------------------------------------------------
# Debug toolbar / dev extras (optional)
# ---------------------------------------------------------------------------

INTERNAL_IPS = [
    "127.0.0.1",
]
