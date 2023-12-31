from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from services.models import Subscription, Plan


class PlanSerializer(ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(ModelSerializer):
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    email = serializers.CharField(source='client.user.email', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan_id', 'client_name', 'email', 'plan', 'price']
