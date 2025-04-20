import json
import redis
from datetime import datetime
from django.db.models import Sum, Count, Case, When, Value, IntegerField, DecimalField
from django.db.models.functions import Coalesce
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection
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
        # Get all active connections for the company
        connection_id = cache.get(f"company:{company.id}:connections", version=1)

        # Get filters for the connection
        filters_str = cache.get(f"connection_filters:{connection_id}")

        if not filters_str:
            filters = {}
        else:
            filters_str = filters_str.decode() if isinstance(filters_str, bytes) else filters_str
            try:
                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                print(f"Invalid filter format for connection {connection_id}")
                filters = {}

        start_date = end_date = agent_id = None

        if "date_range" in filters and filters["date_range"]:
            start_date, end_date = filters["date_range"]

        if "agent_id" in filters:
            agent_id = filters["agent_id"]

        metrics = compute_metrics(
            company=company,
            agent_id=agent_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Send metrics to consumer
        try:
            async_to_sync(channel_layer.group_send)(
                f"metrics_{company.id}",
                {
                    "type": "send_metrics",
                    "data": metrics,
                    "timestamp": datetime.now().isoformat(),
                    "connection_id": connection_id
                },
            )
        except Exception as e:
            print(f"Failed to send metrics to group: {e}")

    return "Company metrics broadcast complete"


def compute_metrics(company, start_date=None, end_date=None, agent_id=None):
    """Compute metrics for a given company."""

    filters = {"agent_id__company": company}

    if start_date and end_date:
        filters["created_at__range"] = [start_date, end_date]
    elif start_date:
        filters["created_at__range"] = start_date
    elif end_date:
        filters["created_at__lte"] = end_date

    if agent_id:
        filters["agent_id"] = agent_id

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

    aggregates["total_amount"] = float(aggregates["total_amount"])

    top_agents = (
        transactions.values("agent_id")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )

    metrics = {**aggregates, "top_agents": list(top_agents)}

    return metrics


@shared_task
def test_task():
    print("Task ran")
