from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'photo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        
    def create(self, validated_data):
        agent = self.context['request'].user.agent
        validated_data['created_by'] = agent
        return super().create(validated_data)