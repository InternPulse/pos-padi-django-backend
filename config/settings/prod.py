from .base import *  # noqa
import dj_database_url


DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
    )
}
