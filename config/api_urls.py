# All urls that are to be in the format api/v1/
from django.urls import path, include

urlpatterns = [
path("", include("apps.companies.urls"))
]