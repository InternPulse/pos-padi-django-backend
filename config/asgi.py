"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.companies.middleware import ConnectionTrackerStack
from apps.companies.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": ConnectionTrackerStack(URLRouter(websocket_urlpatterns)),
    }
)
