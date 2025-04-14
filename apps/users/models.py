from django.db import models
import random
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from ..common.models import BaseModel
from ..common.validators import phone_validator, validate_image_size
from ..companies.models import Company


class UserManager(BaseUserManager):

    def create_user(
        self, email, password, first_name, last_name, phone, nin, role, **extra_fields
    ):

        if not all([email, password, first_name, last_name, phone, nin, role]):
            raise ValueError("All fields are required.")

        if role not in ["owner", "agent", "customer"]:
            raise ValidationError(
                "Role must be either 'owner', 'agent', or 'customer'."
            )

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(f"Invalid password: {e.messages}")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            nin=nin,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save()
        return user

    def create_superuser(
        self, email, password, first_name, last_name, phone, nin, role, **extra_fields
    ):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(
            email, password, first_name, last_name, phone, nin, role, **extra_fields
        )

        if not user.is_staff:
            raise ValueError("Superuser must have is_staff=True.")
        if not user.is_superuser:
            raise ValueError("Superuser must have is_superuser=True.")

        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("customer", "Customer"),
        ("agent", "Agent")
    ]

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone = models.CharField(max_length=15, blank=False, validators=[phone_validator])
    photo = models.ImageField(validators=[validate_image_size])
    national_id_front = models.ImageField(validators=[validate_image_size])
    national_id_back = models.ImageField(validators=[validate_image_size])
    nin = models.CharField(max_length=11, validators=[MinLengthValidator(11)], blank=False)
    role = models.CharField(max_length=10, blank=False, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone",
        "nin",
        "role",
        "photo",
        "national_id_front",
        "national_id_back",
    ]

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return f"{self.email}"

def generate_agent_id():
    """function to generate agent_id"""
    return random.randint(100000, 999999)

class Agent(BaseModel):
    """This is a class for the agent models"""

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    agent_id = models.IntegerField(unique=True, max_digits=6, default=generate_agent_id)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False)
    commission = models.DecimalField(max_digits=10, decimal_places=5, auto_round=True)
    rating = models.DecimalField(max_digits=10, decimal_places=3, auto_round=True)
    status = models.CharField(max_length=20, default="active")

    class Meta:
        ordering = ["agent_id"]

    def __str__(self):
        return f"{self.agent_id}"