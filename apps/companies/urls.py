from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)

urlpatterns = [
    path("", include(router.urls))
]