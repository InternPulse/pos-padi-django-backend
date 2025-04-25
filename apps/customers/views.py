from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models  # Import models for database operations
from .models import Customer
from .serializers import CustomerSerializer
from ..users.permissions import IsOwnerOrAgentOrSuperuser, IsAgentOrSuperuser
from ..external_tables.serializers import TransactionSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Customer.objects.none()  # Return an empty queryset for schema generation
        if self.request.user.is_superuser:
            return Customer.objects.all()
        elif self.request.user.role == "agent":
            return Customer.objects.filter(created_by=self.request.user.agent)
        elif self.request.user.role == "owner":
            return Customer.objects.filter(created_by__company=self.request.user.company)
    
    def get_permissions(self):
        if self.action in ["create"]:
            permissions = [IsAgentOrSuperuser]
        else:
            permissions = [IsOwnerOrAgentOrSuperuser]
        return [permission() for permission in permissions]
    
    def get_serializer_context(self):
        context= super().get_serializer_context()
        context['request'] = self.request
        return context

    @swagger_auto_schema(
        operation_summary="List all customers",
        operation_description="Retrieve a list of all customers. Only superusers can view all customers, while other users can only view their own customers.",
        responses={
            200: "List of customers retrieved successfully.",
            403: "Permission denied.",
        },
    )
    def list(self, request, *args, **kwargs):
        """List all customers."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific customer",
        operation_description="Retrieve details of a specific customer by their ID.",
        responses={
            200: "Customer details retrieved successfully.",
            404: "Customer not found.",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific customer."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new customer",
        operation_description="Create a new customer by providing the required details.",
        request_body=CustomerSerializer,
        responses={
            201: "Customer created successfully.",
            400: "Invalid data provided.",
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new customer."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a specific customer",
        operation_description="Update details of a specific customer by their ID.",
        request_body=CustomerSerializer,
        responses={
            200: "Customer updated successfully.",
            400: "Invalid data provided.",
            404: "Customer not found.",
        },
    )
    def update(self, request, *args, **kwargs):
        """Update a specific customer."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a specific customer",
        operation_description="Partially update details of a specific customer by their ID.",
        request_body=CustomerSerializer,
        responses={
            200: "Customer partially updated successfully.",
            400: "Invalid data provided.",
            404: "Customer not found.",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a specific customer."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a specific customer",
        operation_description="Delete a specific customer by their ID.",
        responses={
            204: "Customer deleted successfully.",
            404: "Customer not found.",
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a specific customer."""
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve transactions for a specific customer",
        operation_summary="Customer transactions",
        responses={200: TransactionSerializer(many=True)},
    )
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None, *args, **kwargs):
        customer = self.get_object()
        transactions = customer.transactions
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve a summary of transactions for a specific customer",
        operation_summary="Transaction summary",
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
    def transaction_summary(self, request, pk=None, *args, **kwargs):
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