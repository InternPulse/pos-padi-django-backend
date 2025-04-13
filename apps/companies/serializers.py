from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework import serializers
from .models import Company
from ..users.models import User
from ..users.serializers import UserSerializer


class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    user = UserSerializer

    class Meta:
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at", "is_active"]

    def validate(self, attrs):
        super.validate(attrs)

        if "user" in attrs and attrs["user"].get("role") != "owner":
            raise serializers.ValidationError({"role": "User must have role 'owner'"})
        
        if self.instance and "registration_number" in attrs:
            raise serializers.ValidationError(
                {"registration_number": "This field cannot be modified after creation"}
            )
        
        if self.instance and "name" in attrs:
            raise serializers.ValidationError(
                {"name": "This field cannot be modified after creation"}
            )

        return attrs
    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_data["role"] = "owner" # Force role="owner"

        user = User.objects.create_user(**user_data)

        company = Company.objects.create(owner=user, **validated_data)

        return company