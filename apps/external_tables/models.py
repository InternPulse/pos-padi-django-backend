"""
Models for external database tables managed by other systems.
WARNING: Do not modify schemas (managed=False)!
"""

from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator
from ..common.models import BaseModel
from ..companies.models import Company
from ..users.models import User


class Agent(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    agent_id = models.CharField(max_length=6)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=False)
    commission = models.DecimalField(
        decimal_places=2,
        max_digits=3,
        blank=False,
        validators=[MaxValueValidator(1.00),],
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=False)
    status = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "agents"


class Customer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=False, related_name="user")
    loyalty_points = models.ManyToManyField(Company, through="CompanyLoyaltyPoints", related_name="loyalty_points")
    tag = models.CharField(max_length=10)


class Transaction(BaseModel):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, blank=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
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