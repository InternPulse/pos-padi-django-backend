# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        validators=[validate_password],
    )

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
            "national_id_front",
            "national_id_back",
            "password",
        ]
        extra_kwargs = {
            "photo": {"required": True},
            "national_id_front": {"required": True},
            "national_id_back": {"required": True},
        }

    def validate(self, data):
        if data["role"] not in ["owner", "agent", "customer"]:
            raise serializers.ValidationError("Invalid role.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            nin=validated_data["nin"],
            role=validated_data["role"],
            photo=validated_data["photo"],
            national_id_front=validated_data["national_id_front"],
            national_id_back=validated_data["national_id_back"],
        )
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            print(f"Authentication failed for email: {data['email']}")  # Debugging log
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            print(f"Email not verified for user: {data['email']}")  # Debugging log
            raise serializers.ValidationError("Email is not verified.")
        return user
