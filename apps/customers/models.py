from django.db import models
from django.core.validators import RegexValidator
from ..common.models import BaseModel
from ..users.models import User
from ..agents.models import Agent
from ..companies.models import Company
import random


class Customer(BaseModel):
    TAG_CHOICES = [
        ("vip", "VIP"),
        ("frequent", "Frequent"),
        ("regular", "Regular"),
        ("inactive", "Inactive"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=6, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="customer_photos/", null=True, blank=True)
    # created_by = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name='customers')
    tag = models.CharField(
        max_length=10,
        choices=TAG_CHOICES,
        default="regular",
        help_text="Customer classification for segmentation",
    )
    loyalty_points = models.ManyToManyField(
        through="CustomerLoyaltyPoints", related_name="loyalty_points", to=Company
    )

    @property
    def transactions(self):
        return self.customer_transactions.all().order_by("-created_at")

    @property
    def transaction_count(self):
        return self.customer_transactions.count()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.customer_id})"

    def save(self, *args, **kwargs):
        if not self.customer_id:
            # Generate a unique 6-digit customer ID
            while True:
                customer_id = str(random.randint(100000, 999999))
                if not Customer.objects.filter(customer_id=customer_id).exists():
                    self.customer_id = str(customer_id)
                    break
        super().save(*args, **kwargs)


class CustomerLoyaltyPoints(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    loyalty_points = models.IntegerField(default=0)

    class Meta:
        unique_together = (("company", "customer"),)
