"""
Models for external database tables managed by other systems.
WARNING: Do not modify schemas (managed=False)!
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator
from ..common.models import BaseModel
from ..companies.models import Company
from ..users.models import User
from ..agents.models import Agent


class Customer(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, related_name="user", null=True
    )
    loyalty_points = models.ManyToManyField(
        Company,
        through="CompanyLoyaltyPoints",
        related_name="loyalty_points",
        null=True,
    )
    tag = models.CharField(max_length=10, null=True)

    class Meta:
        managed = False
        db_table = "customers"


class Transaction(BaseModel):
    agent_id = models.ForeignKey(
        Agent, on_delete=models.PROTECT, blank=False, null=True
    )
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    type = models.CharField(max_length=10, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    status = models.CharField(max_length=20, null=True)

    class Meta:
        managed = False
        db_table = "transactions"


class CompanyLoyaltyPoints(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    loyalty_points = models.IntegerField(validators=[MinLengthValidator(0)])

    class Meta:
        managed = False
        db_table = "company_loyalty_points"
        unique_together = (("company", "customer"),)
