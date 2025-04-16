from django.db import models
from django.core.validators import RegexValidator
from ..common.models import BaseModel
from ..agents.models import Agent

class Customer(BaseModel):
    name = models.CharField(max_length=100)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17)
    photo = models.ImageField(upload_to='customer_photos/', null=True, blank=True)
    created_by = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name='customers')

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.phone})"