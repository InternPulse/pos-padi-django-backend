from django.db import transaction
from django.db.models import Sum, Count, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Company
from .serializers import CompanySerializer
from .utils import send_deactivation_emails
from ..users.permissions import IsOwnerOrSuperuser
from ..agents.models import Agent
from ..external_tables.models import Agent, Transaction


class CompanyViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrSuperuser]
    queryset = Company.objects.none()
    serializer_class = CompanySerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        try:
            return Company.objects.filter(
                owner=self.request.user, is_active=True
            ).select_related("owner")
        except AttributeError:
            return Company.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        Agent.objects.filter(company=company, user__role="agent").update(
            role="customer"
        )

        company.owner.role = "customer"
        company.owner.save(update_fields=["role"])

        company.deactivate()

        # Delay sending emails till changes commited to dB
        transaction.on_commit(lambda: send_deactivation_emails(company, request.user))
        return Response(
            {
                "detail": "Company deactivated successfully",
                "actions": {
                    "agents_downgraded": Agent.objects.filter(
                        company=company, user__role="customer"
                    ).count(),
                    "terminals_deactivated": Terminal.objects.filter(
                        company_id=company.id, is_active=False
                    ).count(),
                },
            },
            status=status.HTTP_200_OK,
        )


class CompanyMetricsView(APIView):

    permission_classes = [IsOwnerOrSuperuser]

    def get(self, request, **kwargs):
        """
        GET /api/v1/companies/dashboard/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&agent_id=123456
        """

        company = get_object_or_404(Company, owner=request.user.id)

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
            filters = {"agent_id__company": company, "created_at__range": date_range}
        else:
            filters = {"agent_id__company": company}

        agent_id = request.query_params.get("agent_id")
        if agent_id:
            try:
                Agent.objects.get(agent_id=agent_id, company=company)
                filters["agent_id"] = agent_id
            except Agent.DoesNotExist:
                return Response(
                    {
                        "message": "Agent not found",
                        "error": "Agent with the provided ID does not exist in this company.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        transactions = Transaction.objects.filter(**filters).select_related(
            "agent_id", "customer_id"
        )
        aggregates = transactions.aggregate(
            total_transactions=Count("id"),
            total_successful=Coalesce(
                Sum(
                    Case(
                        When(status="completed", then=1),
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
            total_amount=Coalesce(Sum("amount"), Value(0, output_field=DecimalField())),
            total_agents=Count("agent_id", distinct=True),
            total_customers=Count("customer_id", distinct=True),
        )

        top_agents = (
            transactions.values("agent_id")
            .annotate(total=Sum("amount"))
            .order_by("-total")[:5]
        )

        metrics = {**aggregates, "top_agents": list(top_agents)}

        return Response({"message": "Metrics retrieved successfully", "data": metrics})
