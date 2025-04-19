from django.db import models
from django.core.validators import MinValueValidator
from ..common.models import BaseModel
from ..companies.models import Company
from ..users.models import User
import random


class Agent(BaseModel):
    """This is a class for the pos agent tables"""

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, related_name="agent")
    agent_id = models.IntegerField(unique=True, validators=[MinValueValidator(100000)], null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    commission = models.DecimalField(max_digits=10, decimal_places=5,)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    status = models.CharField(max_length=20, default="inactive")

    class Meta:
        ordering = ["agent_id"]

    def __str__(self):
        return f"{self.agent_id}"

    def save(self, *args, **kwargs):
        if not self.agent_id:
            while True:
                agent_id = random.randint(100000, 999999)
                if not Agent.objects.filter(agent_id=agent_id).exists():
                    self.agent_id = agent_id
                    break
        super().save(*args, **kwargs)

