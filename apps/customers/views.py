from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
from ..users.permissions import IsAgentOrSuperuser
from ..external_tables.serializers import TransactionSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAgentOrSuperuser]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Customer.objects.all()
        return Customer.objects.filter(created_by=self.request.user.agent)
    
    def get_serializer_context(self):
        context= super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        customer = self.get_object()
        transactions = customer.transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transaction_summary(self, request, pk=None):
        customer = self.get_object()
        summary = {
            'total_transactions': customer.transaction_count,
            'successful_transactions': customer.customer_transactions.filter(status='successful').count(),
            'failed_transactions': customer.customer_transactions.filter(status='failed').count(),
            'total_amount': customer.customer_transactions.filter(status='successful').aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
        }
        return Response(summary)