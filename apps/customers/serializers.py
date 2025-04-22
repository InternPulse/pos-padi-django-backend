from rest_framework import serializers
from .models import Customer
from ..users.serializers import RegistrationSerializer
from ..external_tables.serializers import TransactionSerializer

class CustomerSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    user = RegistrationSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id', 'user', 'customer_id', 'first_name', "last_name",
            'photo', 'tag', 'loyalty_points', 'transactions',
            'transaction_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_id', 'created_at', 
            'updated_at', 'created_by', 'loyalty_points'
        ]

    def create(self, validated_data):
        agent = self.context['request'].user.agent
        validated_data['created_by'] = agent
        return super().create(validated_data)