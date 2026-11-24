from .base import *

DEBUG = env.bool("DEBUG", default=True)
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-dev-key-pulseapi-test-environment-382910-do-not-use-in-prod",
)
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0", "testserver"],
)

# Postgres ONLY — per Phase 0 Review Fix 4: no SQLite fallback
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://pulseapi:pulseapi_dev_password@localhost:5432/pulseapi",
    )
}
