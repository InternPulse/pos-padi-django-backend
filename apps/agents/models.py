from django.db import models
from django.core.validators import MinValueValidator
import random
from ..common.models import BaseModel
from ..companies.models import Company
from ..users.models import User


class Agent(BaseModel):
    """This is a class for the pos agent tables"""

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    agent_id = models.IntegerField(unique=True, max_length=6, validators=[MinValueValidator(100000)])
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    commission = models.DecimalField(max_digits=10, decimal_places=5, auto_round=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, auto_round=True)
    status = models.CharField(max_length=20, default="inactive")

    class Meta:
        ordering = ["agent_id"]

    def __str__(self):
        return f"{self.agent_id}"


def generate_agent_id():
    """method to generate the agent_id"""
    while Agent.objects.filter(agent_id=agent_id).exists():
        agent_id = random.randint(100000, 999999)
    return agent_id

