from datetime import datetime
from django.db import transaction
from django.db.models import (
    Q,
    Sum,
    Count,
    Case,
    When,
    Value,
    IntegerField,
    DecimalField,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
            ).select_related("owner").order_by("id")
        except AttributeError:
            return Company.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        company = self.get_object()

        # Update agents to remove their association with the company
        Agent.objects.filter(company=company).update(company=None)

        company.owner.role = "customer"
        company.owner.save(update_fields=["role"])

        company.deactivate()

        # Delay sending emails till changes committed to the DB
        transaction.on_commit(lambda: send_deactivation_emails(company, request.user))
        return Response(status=status.HTTP_204_NO_CONTENT)


# Swagger documentation for CompanyViewSet
CompanyViewSet.list = swagger_auto_schema(
    operation_summary="Retrieve companies",
    operation_description="Retrieve a list of companies owned by the authenticated user.",
    responses={
        200: "List of companies retrieved successfully.",
        403: "Permission denied.",
    },
)(CompanyViewSet.list)

CompanyViewSet.retrieve = swagger_auto_schema(
    operation_summary="Retrieve a specific company",
    operation_description="Retrieve details of a specific company by its ID.",
    responses={
        200: "Company details retrieved successfully.",
        404: "Company not found.",
    },
)(CompanyViewSet.retrieve)

CompanyViewSet.create = swagger_auto_schema(
    operation_summary="Create a new company",
    operation_description="Create a new company by providing the required details.",
    request_body=CompanySerializer,
    responses={
        201: "Company created successfully.",
        400: "Invalid data provided.",
    },
)(CompanyViewSet.create)

CompanyViewSet.update = swagger_auto_schema(
    operation_summary="Update a specific company",
    operation_description="Update details of a specific company by its ID.",
    request_body=CompanySerializer,
    responses={
        200: "Company updated successfully.",
        400: "Invalid data provided.",
        404: "Company not found.",
    },
)(CompanyViewSet.update)

CompanyViewSet.partial_update = swagger_auto_schema(
    operation_summary="Partially update a specific company",
    operation_description="Partially update details of a specific company by its ID.",
    request_body=CompanySerializer,
    responses={
        200: "Company partially updated successfully.",
        400: "Invalid data provided.",
        404: "Company not found.",
    },
)(CompanyViewSet.partial_update)

CompanyViewSet.destroy = swagger_auto_schema(
    operation_summary="Delete a specific company",
    operation_description="Deactivate a specific company by its ID.",
    responses={
        200: "Company deactivated successfully.",
        404: "Company not found.",
    },
)(CompanyViewSet.destroy)


class CompanyMetricsView(APIView):

    permission_classes = [IsOwnerOrSuperuser]

    def get(self, request, **kwargs):
        """
        GET /api/v1/companies/dashboard/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&agent_id=123456
        """

        company = get_object_or_404(Company, owner=request.user.id)
        agents = Agent.objects.filter(company=company).values_list("agent_id", flat=True)
        if not agents:
            return Response(
                {
                    "message": "No agents found",
                    "error": "No agents associated with this company.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            if start_date and end_date:
                start_date_obj = parse_date(start_date)
                end_date_obj = parse_date(end_date)
                print(end_date)

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
                date_range = [start_date_obj, datetime.now().isoformat()]

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
            filters = {"agent_id__in": agents, "created_at__range": date_range}
        else:
            filters = {"agent_id__in": agents}

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
            total_agents=Count("agent_id", distinct=True),
            total_customers=Count("customer_id", distinct=True),
        )

        if not agent_id:
            top_agents = (
                transactions.values("agent_id")
                .annotate(total=Sum("amount"))
                .order_by("-total")[:5]
            )

            metrics = {**aggregates, "top_agents": list(top_agents)}

        return Response({"message": "Metrics retrieved successfully", "data": metrics})


# Swagger documentation for CompanyMetricsView
CompanyMetricsView.get = swagger_auto_schema(
    operation_summary="Retrieve company metrics",
    operation_description="Retrieve metrics for a company, optionally filtered by date range and agent ID.",
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
        openapi.Parameter(
            "agent_id",
            openapi.IN_QUERY,
            description="Agent ID for filtering metrics.",
            type=openapi.TYPE_STRING,
        ),
    ],
    responses={
        200: "Metrics retrieved successfully.",
        400: "Invalid date format or other errors.",
        404: "Agent not found.",
    },
)(CompanyMetricsView.get)