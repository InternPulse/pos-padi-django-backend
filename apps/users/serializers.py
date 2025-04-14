from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import User
import requests
from django.utils import timezone

# Assuming Node.js endpoint configuration
NODEJS_API_URL = "http://localhost:3000/api/transactions"  # Replace with actual Node.js API URL

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "nin",
            "role"
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user





class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=["income", "expense"])
    terminal = serializers.CharField(max_length=100, required=False, allow_blank=True)
    agent_id = serializers.IntegerField(required=False, allow_null=True)
    user_id = serializers.IntegerField()
    created_at = serializers.DateTimeField(default=timezone.now)

    def validate(self, data):
        if data["amount"] <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})
        
        if data.get("agent_id"):
            try:
                User.objects.get(id=data["agent_id"], role="agent")
            except User.DoesNotExist:
                raise serializers.ValidationError({"agent_id": "Invalid agent ID."})
        
        return data

    def create(self, validated_data):
        try:
            response = requests.post(NODEJS_API_URL, json=validated_data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise serializers.ValidationError({"error": f"Failed to create transaction: {str(e)}"})

    def update(self, instance, validated_data):
        try:
            transaction_id = instance["id"]
            response = requests.put(
                f"{NODEJS_API_URL}/{transaction_id}",
                json=validated_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise serializers.ValidationError({"error": f"Failed to update transaction: {str(e)}"})

