"""
Models for external database tables managed by other systems.
WARNING: Do not modify schemas (managed=False)!
"""

from django.db import models
from django.conf import settings
from ..common.models import BaseModel
from ..agents.models import Agent
from ..customers.models import Customer
from ..users.models import User


class Transaction(BaseModel):
    STATUS_CHOICES = [
        ("successful", "Successful"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    ]

    agent_id = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        related_name="transactions",
        db_column="agent_id",
    )
    customer_id = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        null=True,
        related_name="customer_transactions",
        db_column="customer_id",
    )
    description = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    type = models.CharField(max_length=10, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", null=True
    )

    class Meta:
        managed = not settings.TESTING  # Enable management during testing
        db_table = "transactions"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True)
    user_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="notifications",
        db_column="user_id",
        null=True,
    )
    title = models.TextField()
    message = models.TextField()
    data = models.JSONField()
    delivered_at = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.CharField(max_length=255)
    read_at = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = "notifications"


class Dispute(BaseModel):
    transaction_id = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name="dispute",
        db_column="transaction_id",
        null=True,
    )
    status = models.CharField(max_length=50, null=True)
    resolution_notes = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = "disputes"