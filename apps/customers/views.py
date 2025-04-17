from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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

    @swagger_auto_schema(
        operation_description="Retrieve transactions for a specific customer",
        responses={200: TransactionSerializer(many=True)},
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        customer = self.get_object()
        transactions = customer.transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a summary of transactions for a specific customer",
        responses={200: openapi.Response(
            description="Transaction summary",
            examples={
                "application/json": {
                    "total_transactions": 10,
                    "successful_transactions": 8,
                    "failed_transactions": 2,
                    "total_amount": 1500.00
                }
            }
        )},
    )
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