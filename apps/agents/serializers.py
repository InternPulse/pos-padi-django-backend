from rest_framework import serializers
from .models import Agent, generate_agent_id
from ..users.serializers import RegistrationSerializer
from ..companies.models import Company


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for the Agent model"""
    email = serializers.EmailField(required=True, write_only=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Agent
        fields = (
            "company",
            "commission",
            "rating",
            "status",
            "email",
            "first_name",
            "last_name",
            "phone",
        )
        read_only_fields = ["company"]

    def create(self, validated_data):
        company = self.context["request"].user.company
        if not company:
            raise serializers.ValidationError("Company not found")
        validated_data["company"] = company

        user_data = {
            "email": validated_data.pop("email"),
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "phone": validated_data.pop("phone"),
        }

        user_serializer = RegistrationSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        user.set_unusable_password()
        user.save()

        agent = Agent.objects.create(user=user, **validated_data)
        agent.agent_id = generate_agent_id()
        agent.save()
        return agent