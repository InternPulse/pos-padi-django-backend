from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db import transaction
from rest_framework import serializers
from .models import Company
from ..users.models import User
from ..users.serializers import RegistrationSerializer


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at", "is_active", "owner"]

    def validate(self, attrs):
        super().validate(attrs)

        if self.instance and "name" in attrs:
            raise serializers.ValidationError(
                {"name": "This field cannot be modified after creation"}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != "owner":
            raise serializers.ValidationError(
                {"error": _("Only owners can create companies.")}
            )
        if Company.objects.filter(owner=user).exists():
            raise serializers.ValidationError(
                {"error": _("User already has a company.")}
            )
        validated_data["owner"] = user
        company = Company.objects.create(**validated_data)

        return company
