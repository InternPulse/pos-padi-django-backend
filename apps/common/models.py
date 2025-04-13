from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


# Base Model providing common fields and methods
# for all models in the application.
class BaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract=True

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

