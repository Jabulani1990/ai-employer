"""
💰 FINANCIAL MANAGEMENT MODELS

Django models for comprehensive financial management including:
- Tenants and leases  
- Payment tracking
- Late fees
- Financial transactions
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from ai_workers.ai_property_manager.models import PropertyListing
from business.models import Business, AIEmployer


class Tenant(models.Model):
    """Tenant information for property rentals"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 🏢 BUSINESS ISOLATION: Connect tenant to specific business
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tenants')
    ai_employer = models.ForeignKey(AIEmployer, on_delete=models.CASCADE, related_name='tenants', null=True, blank=True)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Contact information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Tenant status
    is_active = models.BooleanField(default=True)
    credit_score = models.IntegerField(null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_tenants'
        app_label = 'ai_property_manager'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Lease(models.Model):
    """Lease agreements for property rentals"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_listing = models.ForeignKey(PropertyListing, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    
    # Lease terms
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Payment schedule
    rent_due_day = models.IntegerField(default=1, help_text="Day of month rent is due (1-31)")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_leases'
        app_label = 'ai_property_manager'
        
    def __str__(self):
        return f"Lease: {self.property_listing.title} - {self.tenant.full_name}"
    
    @property
    def is_active_lease(self):
        return self.status == 'active' and self.start_date <= timezone.now().date() <= self.end_date
    
    def get_days_until_due(self):
        """Calculate days until next rent payment"""
        today = timezone.now().date()
        
        # Find next due date
        if today.day <= self.rent_due_day:
            # This month
            try:
                next_due = today.replace(day=self.rent_due_day)
            except ValueError:
                # Handle cases where rent_due_day doesn't exist in current month
                next_due = today.replace(day=min(self.rent_due_day, 28))
        else:
            # Next month
            if today.month == 12:
                try:
                    next_due = today.replace(year=today.year + 1, month=1, day=self.rent_due_day)
                except ValueError:
                    next_due = today.replace(year=today.year + 1, month=1, day=min(self.rent_due_day, 28))
            else:
                try:
                    next_due = today.replace(month=today.month + 1, day=self.rent_due_day)
                except ValueError:
                    next_due = today.replace(month=today.month + 1, day=min(self.rent_due_day, 28))
        
        return (next_due - today).days


class Payment(models.Model):
    """Payment records for rent and other charges"""
    
    PAYMENT_TYPES = [
        ('rent', 'Rent Payment'),
        ('late_fee', 'Late Fee'),
        ('security_deposit', 'Security Deposit'),
        ('maintenance', 'Maintenance Fee'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='rent')
    payment_date = models.DateField()
    due_date = models.DateField()
    
    # Payment tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Notes
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_payments'
        app_label = 'ai_property_manager'
        ordering = ['-due_date']
        
    def __str__(self):
        return f"Payment: {self.lease.tenant.full_name} - ${self.amount} ({self.payment_type})"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status in ['pending']
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class LateFee(models.Model):
    """Late fee charges for overdue payments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('waived', 'Waived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='late_fees')
    
    # Fee details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    days_overdue = models.IntegerField()
    fee_date = models.DateField(auto_now_add=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    waive_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_late_fees'
        app_label = 'ai_property_manager'
        
    def __str__(self):
        return f"Late Fee: {self.payment.lease.tenant.full_name} - ${self.amount}"


class PaymentReminder(models.Model):
    """Payment reminder notifications sent to tenants"""
    
    REMINDER_TYPES = [
        ('upcoming', 'Upcoming Payment'),
        ('overdue', 'Overdue Payment'),
        ('late_fee', 'Late Fee Notice'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='reminders')
    
    # Reminder details
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    
    # Message content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'financial_payment_reminders'
        app_label = 'ai_property_manager'
        ordering = ['-scheduled_date']
        
    def __str__(self):
        return f"Reminder: {self.payment.lease.tenant.full_name} - {self.reminder_type}"


class FinancialReport(models.Model):
    """Generated financial reports"""
    
    REPORT_TYPES = [
        ('monthly_summary', 'Monthly Summary'),
        ('payment_status', 'Payment Status Report'),
        ('overdue_report', 'Overdue Payments Report'),
        ('annual_summary', 'Annual Summary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    
    # Report period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report data
    report_data = models.JSONField()  # Stores the generated report data
    file_path = models.CharField(max_length=500, blank=True)  # Path to generated PDF/Excel file
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=100, default='AI Financial Manager')
    
    class Meta:
        db_table = 'financial_reports'
        app_label = 'ai_property_manager'
        ordering = ['-generated_at']
        
    def __str__(self):
        return f"Report: {self.report_type} ({self.start_date} to {self.end_date})"