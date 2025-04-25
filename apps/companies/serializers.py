from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Company
from ..users.models import User
from ..users.serializers import RegistrationSerializer
from ..agents.serializers import AgentSerializer


class CompanySerializer(serializers.ModelSerializer):
    owner = RegistrationSerializer(read_only=True)
    # agents = AgentSerializer(many=True, read_only=True)
    # customers = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at", "is_active", "owner"]

    # def get_customers(self, obj):
    #     customers = User.objects.filter(
    #         customer__customer_transactions__agent_id__company=obj, role="customer"
    #     ).distinct()
    #     return RegistrationSerializer(customers, many=True).data
    
    

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
            print(f"Validation Error: User role is {user.role}, not 'owner'.")
            raise serializers.ValidationError(
                {"error": _(f"Only owners can create companies. User role: {user.role}")}
            )
        if Company.objects.filter(owner=user).exists():
            print(f"Validation Error: User ID {user.id} already owns a company.")
            raise serializers.ValidationError(
                {"error": _(f"User already has a company. User ID: {user.id}")}
            )
        validated_data["owner"] = user
        company = Company.objects.create(**validated_data)

        return company
