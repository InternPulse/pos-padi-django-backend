from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, CompanyMetricsView

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)

urlpatterns = [
    path(
        "companies/dashboard/",
        CompanyMetricsView.as_view(),
        name="company-dashboard",
    ),
    path("", include(router.urls)),
]
