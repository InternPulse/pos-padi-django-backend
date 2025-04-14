from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Company
from .serializers import CompanySerializer
from .utils import send_deactivation_emails
from ..users.permissions import IsOwner
from ..external_tables.models import Agent
from ..external_tables.models import Agent, Transaction


class CompanyViewSet(ModelViewSet):
    permission_classes = [AllowAny]  
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        try:
            return Company.objects.filter(
                id=self.request.user.company.id, is_active=True
            ).select_related("owner")
        except AttributeError:
            return Company.objects.none()

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        Agent.objects.filter(company=company, user__role="agent").update(
            role="customer"
        )

        Terminal.objects.filter(company=company.id).update(is_active=False)

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

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
        )


class CompanyMetricsView(APIView):
    """
    GET /api/vi/companies/<company_id>/metrics/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&agent_id=123456
    """

    def get(self, request, company_id):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "start_date and end_date query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start_date_obj = parse_date(start_date)
        end_date_obj = parse_date(end_date)

        if not start_date_obj or not end_date_obj:
            return Response(
                {"error": "Dates must be in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if start_date_obj > end_date_obj:
            return Response(
                {"error": "start_date cannot be after end_date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = get_object_or_404(
            Company, id=request.user.company.id, owner=request.user
        )

        filters = {
            "agent__company": company,
            "created_at__range": [start_date_obj, end_date_obj],
        }

        if agent_id := request.query_params.get("agent_id"):
            try:
                Agent.objects.get(agent_id=agent_id, company=company)
                filters["agent_id"] = agent_id
            except Agent.DoesNotExist:
                return Response(
                    {
                        "message": "Agent not found",
                        "error": f"Agent with the provided ID does not exist in this company."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        transactions = Transaction.objects.filter(**filters)
        agents = Agent.objects.filter(company=company)

        metrics = {
            "total_transactions": transactions.count(),
            "total_succesful_transactions": transactions.filter(
                status="completed"
            ).count(),
            "total_failed_transactions": transactions.filter(status="failed").count(),
            "total_amount": transactions.aggregate(Sum("amount"))["amount__sum"],
            "total_agents": transactions.values("agent_id").distinct().count(),
            "top_agents": (
                transactions.values("agent_id")
                .annotate(total=Sum("amount"))
                .order_by("-total")
            ),
            "total_customers": transactions.values("customer_id").distinct().count(),
        }

        return Response({"message": "Metrics retrieved successfully", "data": metrics})
