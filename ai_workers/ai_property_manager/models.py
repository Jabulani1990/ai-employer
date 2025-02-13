from django.db import models
import uuid
from PIL import Image
from django.core.files.storage import default_storage

class PropertyListing(models.Model):
    """Stores auto-generated property listings (houses, land, apartments, etc.)"""
    
    PROPERTY_TYPES = [
        ("house", "House"),
        ("land", "Land"),
        ("apartment", "Apartment"),
        ("commercial", "Commercial Property"),
        ("other", "Other"),
    ]
    
    LISTING_TYPES = [
        ("sale", "For Sale"),
        ("rent", "For Rent"),
        ("lease", "For Lease"),
    ]
    
    STATUS_CHOICES = [
        ("available", "Available"),
        ("sold", "Sold"),
        ("pending", "Pending"),
        ("rented", "Rented"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default="sale")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    price = models.DecimalField(max_digits=15, decimal_places=2)
    location = models.CharField(max_length=255)
    
    # House-specific fields (optional for land)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    
    # Area (applies to both houses & land)
    area = models.FloatField(help_text="Area in square meters", null=True, blank=True)
    
    # Additional features stored as JSON
    features = models.JSONField(default=dict, blank=True, help_text="Extra property details")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    is_suspicious = models.BooleanField(default=False)
    property_category = models.CharField(max_length=50, choices=[  # NEW FIELD
        ("Luxury", "Luxury"),
        ("Standard", "Standard"),
        ("Basic", "Basic"),
    ], default="Basic")

    # 🔹 New fields for market analysis
    average_market_price = models.FloatField(null=True, blank=True)
    price_deviation = models.FloatField(null=True, blank=True)
    is_overpriced = models.BooleanField(default=False)
    is_underpriced = models.BooleanField(default=False)
    suggested_price = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.property_type} ({self.listing_type})"
    

class PropertyMedia(models.Model):
    property = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="property_media/")
    file_type = models.CharField(
        max_length=10,
        choices=[("image", "Image"), ("document", "Document")],
        default="image",
    )

    def __str__(self):
        return f"{self.property.title} - {self.file.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Optimize images only using Pillow package
        if self.file_type == "image":
            img = Image.open(self.file.path)

            # Resize if larger than 1080p
            if img.height > 1080 or img.width > 1920:
                output_size = (1920, 1080)
                img.thumbnail(output_size)
                img.save(self.file.path, quality=85, optimize=True)

