from rest_framework import serializers
from .models import AIWorker, BusinessAIWorker

class AIWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIWorker
        fields = "__all__"
        
class BusinessAIWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAIWorker
        fields = "__all__"