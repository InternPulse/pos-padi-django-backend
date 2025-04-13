"""
Models for external database tables managed by other systems.
WARNING: Do not modify schemas (managed=False)!
"""

from django.db import models
from django.core.validators import MinLengthValidator
from ..common.models import BaseModel
from ..companies.models import Company
from ..users.models import User



class Agent(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    agent_id = models.CharField(max_length=6, )


class Terminal(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, blank=False)
    location = models.CharField(max_length=100, blank=False) # Add choices
    status = models.BooleanField(default=False)

    class Meta:
        managed = False # Django will not migrate or managed this table
        db_table = "terminal"
