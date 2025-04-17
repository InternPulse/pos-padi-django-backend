# All urls that are to be in the format api/v1/
from django.urls import path, include

urlpatterns = [
path("", include("apps.companies.urls")),
path("", include("apps.users.urls")),
path("", include("apps.agents.urls")),
path("", include("apps.customers.urls")),
]