from rest_framework import serializers
from .models import Business, AIEmployer

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'email', 'industry_type', 'contact_number']

class AIEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEmployer
        fields = ['id', 'business', 'budget', 'created_at', 'ai_employer_type', 'location', 'industry_category']
