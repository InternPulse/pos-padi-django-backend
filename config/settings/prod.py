from .base import *  # noqa
import dj_database_url


DATABASES = {
    "default": dj_database_url.parse(
        env("DATABASE_URL")),
        "ENGINE": "django.db.backends.mysql",
}
