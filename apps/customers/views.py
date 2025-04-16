from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Customer
from .serializers import CustomerSerializer
from ..users.permissions import IsAgentOrSuperuser

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAgentOrSuperuser]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Customer.objects.all()
        return Customer.objects.filter(created_by=self.request.user.agent)