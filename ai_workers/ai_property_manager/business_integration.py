"""
🏢 BUSINESS AI PROPERTY MANAGER CONFIGURATION

This connects your existing business system to the AI Property Manager
and provides business-specific configuration and isolation.
"""

from django.db import models
from business.models import Business, AIEmployer, BusinessAIWorker
import uuid

class BusinessPropertyManagerConfig(models.Model):
    """Configuration for AI Property Manager per business"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='property_manager_config')
    ai_employer = models.OneToOneField(AIEmployer, on_delete=models.CASCADE, related_name='property_manager_config')
    business_ai_worker = models.OneToOneField(BusinessAIWorker, on_delete=models.CASCADE, related_name='property_manager_config')
    
    # Property Management Settings
    is_active = models.BooleanField(default=True)
    max_properties = models.IntegerField(default=10)  # Based on subscription plan
    max_tenants = models.IntegerField(default=50)
    
    # Financial Management Settings
    financial_management_enabled = models.BooleanField(default=True)
    auto_late_fees = models.BooleanField(default=True)
    late_fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    late_fee_grace_days = models.IntegerField(default=5)
    
    # Reminder Settings
    payment_reminders_enabled = models.BooleanField(default=True)
    reminder_days_advance = models.JSONField(default=list, help_text="Days before due date to send reminders [7, 3, 1]")
    reminder_email_template = models.TextField(blank=True)
    
    # Reporting Settings
    auto_monthly_reports = models.BooleanField(default=True)
    report_recipients = models.JSONField(default=list, help_text="Email addresses for reports")
    
    # Integration Settings
    payment_processor = models.CharField(max_length=50, choices=[
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('square', 'Square'),
        ('manual', 'Manual Only')
    ], default='manual')
    
    payment_processor_config = models.JSONField(default=dict, help_text="API keys and settings")
    
    # Custom Branding
    company_logo = models.ImageField(upload_to='business_logos/', blank=True)
    brand_colors = models.JSONField(default=dict, help_text="Primary and secondary colors")
    email_signature = models.TextField(blank=True)
    
    # Business Rules
    rent_increase_rules = models.JSONField(default=dict)
    eviction_rules = models.JSONField(default=dict)
    maintenance_rules = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Property Manager Config - {self.business.name}"
    
    @property
    def current_property_count(self):
        return self.business.properties.count()
    
    @property
    def current_tenant_count(self):
        return self.business.tenants.count()
    
    @property
    def can_add_property(self):
        return self.current_property_count < self.max_properties
    
    @property
    def can_add_tenant(self):
        return self.current_tenant_count < self.max_tenants


class PropertyManagerDeployment(models.Model):
    """Tracks AI Property Manager deployment status for businesses"""
    
    DEPLOYMENT_STATUS = [
        ('requested', 'Deployment Requested'),
        ('configuring', 'Configuring'),
        ('deploying', 'Deploying'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('failed', 'Deployment Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='property_manager_deployment')
    ai_employer = models.OneToOneField(AIEmployer, on_delete=models.CASCADE, related_name='property_manager_deployment')
    
    status = models.CharField(max_length=20, choices=DEPLOYMENT_STATUS, default='requested')
    deployment_started = models.DateTimeField(auto_now_add=True)
    deployment_completed = models.DateTimeField(null=True, blank=True)
    
    # Deployment logs
    deployment_logs = models.JSONField(default=list)
    error_message = models.TextField(blank=True)
    
    # Usage tracking
    total_properties_managed = models.IntegerField(default=0)
    total_tenants_managed = models.IntegerField(default=0)
    total_payments_processed = models.IntegerField(default=0)
    total_reminders_sent = models.IntegerField(default=0)
    
    last_activity = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Property Manager Deployment - {self.business.name} ({self.status})"
    
    def add_log(self, message, level='info'):
        """Add deployment log entry"""
        import datetime
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.deployment_logs.append(log_entry)
        self.save()


# Signals to automatically create configurations when business deploys AI Property Manager
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=BusinessAIWorker)
def create_property_manager_config(sender, instance, created, **kwargs):
    """Automatically create configuration when AI Property Manager is deployed"""
    if created and instance.ai_worker.name == "AI Property Manager":
        # Create deployment record
        deployment, created = PropertyManagerDeployment.objects.get_or_create(
            business=instance.business.business,  # BusinessAIWorker.business is User, need Business
            ai_employer=instance.ai_employer,
            defaults={'status': 'configuring'}
        )
        
        # Create configuration
        config, created = BusinessPropertyManagerConfig.objects.get_or_create(
            business=instance.business.business,
            ai_employer=instance.ai_employer,
            business_ai_worker=instance,
            defaults={
                'reminder_days_advance': [7, 3, 1],
                'report_recipients': [instance.business.business.email]
            }
        )
        
        deployment.add_log("Property Manager configuration created")
        deployment.status = 'deploying'
        deployment.save()


class BusinessPropertyManagerUsage(models.Model):
    """Track usage metrics for billing and analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='property_manager_usage')
    
    # Usage period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Activity counters
    properties_managed = models.IntegerField(default=0)
    tenants_managed = models.IntegerField(default=0)
    payments_processed = models.IntegerField(default=0)
    reminders_sent = models.IntegerField(default=0)
    reports_generated = models.IntegerField(default=0)
    api_calls_made = models.IntegerField(default=0)
    
    # Financial metrics
    total_rent_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    late_fees_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['business', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Usage: {self.business.name} ({self.period_start} to {self.period_end})"
