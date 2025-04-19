from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


# Base Model providing common fields and methods
# for all models in the application.


def generate_uuid():
    return str(uuid.uuid4())  # Generate a UUID and convert it to a string

class BaseModel(models.Model):
    id = models.CharField(
        default=generate_uuid, # Generate UUID and convert to string
        editable=False,
        primary_key=True,
        max_length=36,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.pk)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.pk}>"

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=["is_active", "updated_at"] if self.pk else None)

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=["is_active", "updated_at"] if self.pk else None)
