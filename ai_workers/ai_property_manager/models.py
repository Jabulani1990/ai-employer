import os
from django.db import models
import uuid
from PIL import Image, UnidentifiedImageError
from django.core.files.storage import default_storage
from django.utils import timezone
import hashlib

def unique_media_filename(instance, filename):
    """Generate a unique filename using UUID."""
    ext = filename.split(".")[-1]  # Get file extension
    new_filename = f"{uuid.uuid4()}.{ext}"  # Generate new unique filename
    return os.path.join("property_media/", new_filename)

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
    property = models.ForeignKey(
        "ai_property_manager.PropertyListing", on_delete=models.CASCADE, related_name="media"
    )
    file = models.FileField(upload_to=unique_media_filename)
    file_type = models.CharField(
        max_length=10,
        choices=[("image", "Image"), ("document", "Document")],
        default="image",
    )
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.property.title} - {self.file.name}"

    def save(self, *args, **kwargs):
        """Ensure only images are processed and optimize them."""
        super().save(*args, **kwargs)

        if self.file_type == "image" and self.is_valid_image():
            try:
                img = Image.open(self.file.path)
                
                # Resize if larger than 1080p
                if img.height > 1080 or img.width > 1920:
                    output_size = (1920, 1080)
                    img.thumbnail(output_size)
                    img.save(self.file.path, quality=85, optimize=True)
            except UnidentifiedImageError:
                print(f"Skipping optimization: {self.file.name} is not a valid image.")

    def is_valid_image(self):
        """Check if the file extension belongs to an actual image format."""
        valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        ext = os.path.splitext(self.file.name)[1].lower()
        return ext in valid_extensions
    


class TemporaryMedia(models.Model):
    """Stores media files uploaded before property assignment."""
    
    file = models.FileField(upload_to='temporary_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    matched_property = models.ForeignKey(
        "PropertyListing", null=True, blank=True, on_delete=models.CASCADE
    )
    
    # Store hash of title (instead of filename) for better matching
    title_hash = models.CharField(max_length=255, unique=False, blank=True, null=True)

    # Track whether media has been successfully linked to a property
    processed = models.BooleanField(default=False)
    extracted_property_name = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Generate a title hash for matching and extract potential property name."""
        if not self.title_hash:
            self.title_hash = hashlib.md5(self.file.name.encode()).hexdigest()

        if not self.extracted_property_name:
            self.extracted_property_name = self.extract_property_name(self.file.name)

        super().save(*args, **kwargs)

    def extract_property_name(self, filename):
        """Extract property name from the filename (e.g., 'garden_estate-1.jpg' -> 'garden estate')."""
        base_name = os.path.basename(filename)  # Get filename only
        name_part = os.path.splitext(base_name)[0]  # Remove extension
        clean_name = name_part.replace("-", " ").replace("_", " ")  # Normalize spaces
        return clean_name.lower()  # Store in lowercase for case-insensitive matching

    def __str__(self):
        return f"Temporary Media {self.id} - Matched: {self.matched_property is not None}"