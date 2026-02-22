from rest_framework import serializers
from .models import Business, AIEmployer, AIEmployerSettings, Task

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['name', 'email', 'industry_type', 'contact_number']

    def create(self, validated_data):
        """Ensure the owner is set automatically"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['owner'] = request.user  # Assign logged-in user as owner
        return super().create(validated_data)


class AIEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEmployer
        fields = ['id', 'business', 'budget', 'created_at', 'ai_employer_type', 'location', 'industry_category']

    def validate_business(self, business):
        request = self.context.get("request")
        if request and request.user.is_authenticated and business.owner_id != request.user.id:
            raise serializers.ValidationError("You can only register an AI employer for your own business.")
        return business


class AIEmployerSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEmployerSettings
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__' 