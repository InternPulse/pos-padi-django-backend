from .base import *  # noqa
import dj_database_url


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "HOST": env("DB_HOST"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("DB_PORT"),
        "OPTIONS": {
            "ssl": {
                "ca": env("DB_CA_CERT_PATH", default="/etc/secrets/ca-certificate.pem")
            },
        },
    }
}