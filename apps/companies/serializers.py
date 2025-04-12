from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Company
from ..users.models import User


class CompanySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    owner_name = serializers.StringRelatedField(source="owner", read_only=True)
    
    class Meta:
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at", "is_active"]

    def validate_owner(self, value):
        if not value.role == "owner":
            raise serializers.ValidationError(_("Owner must be of role 'owner'"))
        return value

    
        
