from rest_framework import serializers
from django.db import transaction
from ..companies.models import Company
from ..users.models import User
from ..users.serializers import RegistrationSerializer
from .models import Agent


class AgentUserSerializer(serializers.ModelSerializer):
    # Serializer was created to avoid password requirement of RegistrationSerializer
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "nin",
            "role",
            "photo",
        ]
        extra_kwargs = {
            "photo": {"required": False},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_unusable_password()
        user.save()
        return user


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for the Agent model"""
    email = serializers.EmailField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True)
    nin = serializers.CharField(required=True, write_only=True)
    user_id = AgentUserSerializer(read_only=True)
    

    class Meta:
        model = Agent
        fields = "__all__"
        read_only_fields = ["company", "agent_id"]
    


    @transaction.atomic
    def create(self, validated_data):
        owner = self.context["request"].user
        if not owner.company:
            raise serializers.ValidationError("Company not found")
        validated_data["company"] = owner.company

        user_data = {
            "email": validated_data.pop("email"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "phone": validated_data.pop("phone"),
            "nin": validated_data.pop("nin"),
            "role": "agent",
        }

        user_serializer = AgentUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        user.set_unusable_password()
        user.save()

        agent = Agent.objects.create(user_id=user, **validated_data)
        agent.save()
        return agent
