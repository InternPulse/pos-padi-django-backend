from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Company
from ..users.models import User
from ..users.serializers import RegistrationSerializer
from ..agents.serializers import AgentSerializer


class CompanySerializer(serializers.ModelSerializer):
    owner = RegistrationSerializer(read_only=True)

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at", "is_active", "owner"]
    

    def validate(self, attrs):
        super().validate(attrs)

        if self.instance and ("name" in attrs or "owner" in attrs):
            raise serializers.ValidationError(
                {"name": "This field cannot be modified after creation"}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != "owner":
            raise serializers.ValidationError(
                {"error": _(f"Only owners can create companies. User role: {user.role}")}
            )
        if Company.objects.filter(owner=user).exists():
            raise serializers.ValidationError(
                {"error": _(f"User already has a company. User ID: {user.id}")}
            )
        validated_data["owner"] = user
        company = Company.objects.create(**validated_data)

        return company
