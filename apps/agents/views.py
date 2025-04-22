from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum, Count, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Agent
from .serializers import AgentSerializer
from ..users.permissions import IsOwnerOrSuperuser, IsOwnerOrAgentOrSuperuser, IsAgentOrSuperuser
from ..external_tables.models import Transaction


class AgentListCreateView(ListCreateAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Agent.objects.all()
        elif self.request.user.role == "owner":
            print(f"OWNER: {self.request.user.company}") # Debugging line
            return Agent.objects.filter(company=self.request.user.company)
        return Agent.objects.none()

    @swagger_auto_schema(
        operation_summary="List or create agents",
        operation_description="Retrieve a list of agents or create a new agent for the authenticated user's company.",
        responses={
            200: "List of agents retrieved successfully.",
            201: "Agent created successfully.",
            400: "Invalid data provided.",
            403: "Permission denied.",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new agent",
        operation_description="Create a new agent by providing the required details.",
        request_body=AgentSerializer,
        responses={
            201: "Agent created successfully.",
            400: "Invalid data provided.",
            403: "Permission denied.",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AgentRetrieveView(RetrieveAPIView):
    queryset = Agent.objects.none()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return Agent.objects.all()
        elif getattr(user, 'role', None) == "agent":
            return Agent.objects.filter(user=user)
        elif getattr(user, 'role', None) == "owner":
            return Agent.objects.filter(company=user.company)
        return Agent.objects.none()

    @swagger_auto_schema(
        operation_summary="Retrieve a specific agent",
        operation_description="Retrieve details of a specific agent by their ID.",
        responses={
            200: "Agent details retrieved successfully.",
            404: "Agent not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AgentMetricsView(APIView):
    permission_classes = [IsAgentOrSuperuser]

    @swagger_auto_schema(
        operation_summary="Retrieve agent metrics",
        operation_description="Retrieve metrics for a specific agent, optionally filtered by date range.",
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date for filtering metrics (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date for filtering metrics (YYYY-MM-DD).",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: "Metrics retrieved successfully.",
            400: "Invalid date format or other errors.",
            404: "Agent not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        agent = get_object_or_404(Agent, user_id=self.request.user)
        
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            if start_date and end_date:
                start_date_obj = parse_date(start_date)
                end_date_obj = parse_date(end_date)

                if start_date_obj > end_date_obj:
                    return Response(
                        {
                            "message": "Date error",
                            "error": "Start date cannot be after End date",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                date_range = [start_date_obj, end_date_obj]

            elif start_date:
                start_date_obj = parse_date(start_date)
                date_range = [start_date_obj]

            elif end_date:
                end_date_obj = parse_date(end_date)
                date_range = [parse_date("2025-01-01"), end_date]

            else:
                date_range = None

        except (ValueError, TypeError):
            return Response(
                {
                    "message": "Invalid date format",
                    "error": "Invalid date format. Use YYYY-MM-DD.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if date_range:
            filters = {"agent_id": agent.id, "created_at__range": date_range}
        else:
            filters = {"agent_id": agent.id}

        transactions = Transaction.objects.filter(**filters).select_related(
            "agent_id", "customer_id"
        )
        metrics = transactions.aggregate(
            total_transactions=Count("id"),
            total_successful=Coalesce(
                Sum(
                    Case(
                        When(status="successful", then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            ),
            total_failed=Coalesce(
                Sum(
                    Case(
                        When(status="failed", then=1),
                        default=0,
                        output_field=IntegerField(),
                    )
                ),
                Value(0, output_field=IntegerField()),
            ),
            total_amount=Coalesce(
                Sum("amount", filter=Q(status="successful")),
                Value(0, output_field=DecimalField()),
            ),
            total_customers=Count("customer_id", distinct=True)
        )

        return Response(
            {
                "message": "Metrics retrieved successfully",
                "data": metrics
            },
            status=status.HTTP_200_OK
        )
