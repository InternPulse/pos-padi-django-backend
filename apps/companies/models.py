from django.db import models
from ..common.models import BaseModel
from ..users.models  import User
from ..common.validators import validate_image_size


class Company(BaseModel):

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company", blank=False)
    name = models.CharField(max_length=100, unique=True, blank=False)
    state = models.CharField(max_length=100, blank=False)
    lga = models.CharField(max_length=100, blank=False)
    # registration_number = models.CharField(max_length=9, blank=False, unique=True)
    # logo = models.ImageField(null=True, validators=[validate_image_size])

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name