from .base import *  # noqa

SECRET_KEY = env(
    "TEST_SECRET_KEY", default="5bl_5--oxdl7*xo%ca7!0&(3ff6pc5w@doiv5&0@e)q3%prb1v"
)


SWAGGER_USE_COMPAT_RENDERERS = False
