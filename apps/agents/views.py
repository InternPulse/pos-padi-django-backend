from rest_framework.generics import CreateAPIView, RetrieveAPIView
from .models import Agent
from .serializers import AgentSerializer
from ..users.permissions import IsOwnerOrAgentOrSuperuser


class AgentCreateView(CreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    

class AgentRetrieveView(RetrieveAPIView):
    queryset = Agent.objects.none()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
    def get_queryset(self):
        if self.request.user.role == "agent":
            return Agent.objects.filter(user=self.request.user)
        elif self.request.user.role == "owner":
            return Agent.objects.filter(company=self.request.user.company)
        return Agent.objects.none()