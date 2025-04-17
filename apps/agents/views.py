from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Q, Sum, Count, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
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
            return Agent.objects.filter(company=self.request.user.company)
        return Agent.objects.none()


class AgentRetrieveView(RetrieveAPIView):
    queryset = Agent.objects.none()
    serializer_class = AgentSerializer
    permission_classes = [IsOwnerOrAgentOrSuperuser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Agent.objects.all()
        elif self.request.user.role == "agent":
            return Agent.objects.filter(user=self.request.user)
        elif self.request.role =="owner":
            return Agent.objects.filter(company=self.request.user.company)
        return Agent.objects.none()

class AgentMetricsView(APIView):
    permission_classes = [IsAgentOrSuperuser]

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
