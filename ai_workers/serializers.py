from rest_framework import serializers
from .models import AIWorker, BusinessAIWorker


class AIWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIWorker
        fields = "__all__"


class BusinessAIWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAIWorker
        fields = ["id", "business", "ai_employer", "ai_worker", "configurations", "status", "created_at"]
        read_only_fields = ["id", "business", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        business = getattr(getattr(request, "user", None), "business", None)
        ai_employer = attrs.get("ai_employer")

        if business is None:
            raise serializers.ValidationError("Authenticated user must have a registered business profile.")

        if ai_employer and ai_employer.business_id != business.id:
            raise serializers.ValidationError("ai_employer must belong to your business.")

        return attrs
