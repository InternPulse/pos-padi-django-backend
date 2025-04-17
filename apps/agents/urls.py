from django.urls import path,include

from apps.users.urls import urlpatterns
from .views import AgentListCreateView, AgentMetricsView, AgentRetrieveView

urlpatterns = [
    path("agents/", AgentListCreateView.as_view(), name="agent-create"),
    path("agents/<str:pk>/", AgentRetrieveView.as_view(), name="agent-retrieve"),
    path("agents/dashboard/", AgentMetricsView.as_view(), name="agent-dashboard"),
]