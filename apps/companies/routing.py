from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
    re_path(
        r"^ws/companies/dashboard/$",
        consumers.CompanyConsumer.as_asgi(),
        name="company_dashboard",
    ),
]