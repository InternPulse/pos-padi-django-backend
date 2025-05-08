# apps/users/models.py
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.timezone import now
from ..common.models import BaseModel
from ..common.validators import phone_validator, validate_image_size


class UserManager(BaseUserManager):
    def create_user(
        self, email, password, first_name, last_name, phone, role, **extra_fields
    ):
        if not all([email, password, first_name, last_name, phone, role]):
            raise ValueError("All fields are required.")

        if role not in ["owner", "agent", "customer"]:
            raise ValidationError(
                "Role must be either 'owner', 'agent', or 'customer'."
            )

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(f"password: {e.messages}")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save()
        return user

    def create_superuser(
        self, email, password, first_name, last_name, phone, role, **extra_fields
    ):
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(
            email, password, first_name, last_name, phone, role, **extra_fields
        )

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
    photo = models.ImageField(validators=[validate_image_size], blank=True, null=True)
    # national_id_front = models.ImageField(validators=[validate_image_size])
    # national_id_back = models.ImageField(validators=[validate_image_size])
    nin = models.CharField(max_length=11, validators=[MinLengthValidator(11)], blank=False, null=True)
    role = models.CharField(max_length=10, blank=False, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)
    is_email_enabled = models.BooleanField(default=False)
    is_push_notification_enabled = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone",
        "nin",
        "role",
    ]

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return f"{self.email}"

    def is_otp_valid(self):
        return self.otp and self.otp_expiration and self.otp_expiration > now()

