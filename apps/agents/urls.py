from django.urls import path, include
from .views import AgentCreateView


urlpatterns = [
    path("agents/", AgentCreateView.as_view(), name="agent-create"),
]