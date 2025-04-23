from django.urls import path, include

from apps.users.urls import urlpatterns
from .views import (
    AgentListCreateView,
    AgentMetricsView,
    AgentRetrieveView,
    AgentOnboardView,
)

urlpatterns = [
    path("agents/", AgentListCreateView.as_view(), name="agent-create"),
    path("agents/dashboard/", AgentMetricsView.as_view(), name="agent-dashboard"),
    path("agents/onboard/", AgentOnboardView.as_view(), name="agent-onboard-password"),
    path("agents/<str:pk>/", AgentRetrieveView.as_view(), name="agent-retrieve"),
]
