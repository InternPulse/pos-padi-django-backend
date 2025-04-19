from .base import *  # noqa
import dj_database_url


DATABASES = {
    "ENGINE": "django.db.backends.mysql",
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
    ),
}
