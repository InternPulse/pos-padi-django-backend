from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, CompanyMetricsView

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "companies/<uuid:company_id>/metrics",
        CompanyMetricsView.as_view(),
        name="compant-metrics"
    ),
]