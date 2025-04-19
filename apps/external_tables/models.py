"""
Models for external database tables managed by other systems.
WARNING: Do not modify schemas (managed=False)!
"""

from django.db import models
from ..common.models import BaseModel
from ..agents.models import Agent
from ..customers.models import Customer


class Transaction(BaseModel):
    STATUS_CHOICES = [
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    agent_id = models.ForeignKey(
        Agent, on_delete=models.PROTECT, blank=False, null=True
    )
    customer_id = models.ForeignKey(
        Customer, 
        on_delete=models.PROTECT, 
        null=True,
        related_name='customer_transactions'
    )
    description = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    type = models.CharField(max_length=10, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        null=True
    )

    class Meta:
        managed = True
        db_table = "transactions"
