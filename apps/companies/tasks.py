from datetime import datetime
from django.db.models import Sum, Count, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from django.core.cache import cache
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Company
from ..external_tables.models import Transaction
from ..agents.models import Agent


@shared_task
def broadcast_company_metrics():
    """Task to compute and broadcast company metrics"""
    channel_layer = get_channel_layer()

    for company in Company.objects.all():
        #    group_name = f"metrics_{(company.id)}"
        # Get all active connections for the company
        connection_ids = cache.get(f"active_connections_{company.id}", [])

        for connection_id in connection_ids:
            filters = cache.get(f"filters_{connection_id}", {})

            start_date = (
                parse_date(filters.get("start_date")) if filters.get("start_date") else None
            )
            end_date = (
                parse_date(filters.get("end_date")) if filters.get("end_date") else None
            )
            agent_id = filters.get("agent_id") if filters.get("agent_id") else None

            metrics = compute_metrics(
                company=company,
                agent_id=agent_id,
                start_date=start_date,
                end_date=end_date,
            )

            async_to_sync(channel_layer.group_send)(
                f"metrics_{company.id}",
                {
                    "type": "send_metrics",
                    "data": {
                        "company_id": company.id,
                        "metrics": metrics,
                        "timestamp": datetime.now().isoformat(),
                        "connection_id": connection_id,
                    },
                },
            )


def compute_metrics(company, start_date=None, end_date=None, agent_id=None):
    """Compute metrics for a given company."""

    transactions = Transaction.objects.filter(agent_id__company=company).select_related(
        "agent_id", "customer_id"
    )

    if start_date and end_date:
        date_range = [start_date, end_date]
    if start_date:
        date_range = [start_date]
    if end_date:
        date_range = [parse_date("2025-01-01"), end_date]
    else:
        date_range = None

    if date_range:
        filters = {"created_at__range": date_range}
    if agent_id:
        filters["agent_id"] = {"agent_id": agent_id}

    if filters:
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
