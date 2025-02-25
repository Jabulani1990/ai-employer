from rest_framework import serializers
from .models import PropertyListing, PropertyMedia, TemporaryMedia

class PropertyMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyMedia
        fields = ["id", "property", "file", "file_type","uploaded_at"]

class PropertyListingSerializer(serializers.ModelSerializer):
    """Serializer for property details including media"""
    media = PropertyMediaSerializer(many=True, read_only=True)
    class Meta:
        model = PropertyListing
        fields = '__all__'  # Expose all fields in API

class TemporaryMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryMedia
        fields = ["file"]