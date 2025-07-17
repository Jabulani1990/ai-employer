"""
👤 TENANT ACCOUNT MANAGEMENT SYSTEM

Missing piece: Tenant self-service portal and account management
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class TenantAccount(AbstractUser):
    """Extended user model for tenant accounts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to financial tenant record
    financial_tenant = models.OneToOneField(
        'ai_property_manager.Tenant', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='account'
    )
    
    # Account status
    is_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Preferences
    notification_preferences = models.JSONField(default=dict)
    payment_preferences = models.JSONField(default=dict)
    
    # Security
    last_password_change = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Tenant Account: {self.username}"


class TenantPaymentMethod(models.Model):
    """Stored payment methods for tenants"""
    
    PAYMENT_TYPES = [
        ('bank_account', 'Bank Account'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_account = models.ForeignKey(TenantAccount, on_delete=models.CASCADE, related_name='payment_methods')
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Encrypted payment details (use django-encrypted-fields or similar)
    encrypted_details = models.JSONField()  # Store encrypted payment info
    
    # Display info (last 4 digits, etc.)
    display_name = models.CharField(max_length=100)  # "Bank Account ****1234"
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.tenant_account.username} - {self.display_name}"


class TenantNotification(models.Model):
    """Notifications sent to tenants"""
    
    NOTIFICATION_TYPES = [
        ('payment_reminder', 'Payment Reminder'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('late_fee_notice', 'Late Fee Notice'),
        ('lease_renewal', 'Lease Renewal'),
        ('maintenance_update', 'Maintenance Update'),
        ('general', 'General Notice'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_account = models.ForeignKey(TenantAccount, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Delivery
    sent_via_email = models.BooleanField(default=True)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tenant_account.username} - {self.title}"
