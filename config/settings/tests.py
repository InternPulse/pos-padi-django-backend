from .base import *  # noqa

SECRET_KEY = env(
    "TEST_SECRET_KEY", default="5bl_5--oxdl7*xo%ca7!0&(3ff6pc5w@doiv5&0@e)q3%prb1v"
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Add a TESTING flag to indicate the test environment
TESTING = True
