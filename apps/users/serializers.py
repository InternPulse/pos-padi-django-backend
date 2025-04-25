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
            "password",
        ]
        extra_kwargs = {
            "photo": {"required": False},
        }

    def validate(self, data):
        if data["role"] not in ["owner", "agent", "customer"]:
            raise serializers.ValidationError("Invalid role.")
        
        if self.instance and ("email" in data):
            raise serializers.ValidationError(
                {"email": "This field cannot be modified after creation"}
            )
        return data


    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_verified:
            raise serializers.ValidationError("Email is not verified.")
        return user

    class Meta:
        ref_name = "CustomLoginSerializer"  # Unique name to avoid conflicts


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified']
