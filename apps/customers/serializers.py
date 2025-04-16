from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'user', 'customer_id', 'name', 'phone', 
            'photo', 'tag', 'loyalty_points', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_id', 'created_at', 
            'updated_at', 'created_by', 'loyalty_points'
        ]

    def create(self, validated_data):
        agent = self.context['request'].user.agent
        validated_data['created_by'] = agent
        return super().create(validated_data)