from .base import *  # noqa
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "HOST": env("DB_HOST"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "PORT": env("DB_PORT"),
        "OPTIONS": {
            "ssl_mode": "REQUIRED",
            "auth_plugin": "mysql_native_password",
        },
    }
}
