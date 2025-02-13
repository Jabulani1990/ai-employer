from rest_framework import serializers
from .models import PropertyMedia

class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ["id", "property", "file", "file_type"]
