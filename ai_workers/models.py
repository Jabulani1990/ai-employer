import uuid
from django.db import models
from django.contrib.auth import get_user_model
from business.models import AIEmployer
import uuid
from django.utils.timezone import now
from decimal import Decimal

User = get_user_model()

class AIWorker(models.Model):
    """Stores AI Worker templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # e.g., "AI Property Manager"
    industry = models.CharField(max_length=255)  # e.g., "Real Estate"
    job_functions = models.JSONField()  # e.g., ["Property Listing", "Rent Collection"]
    execution_type = models.CharField(max_length=50, choices=[
        ("fully_autonomous", "Fully Autonomous"),
        ("rule_based", "Rule-Based"),
        ("hybrid", "Hybrid AI + Human"),
    ])
    default_config = models.JSONField()  # Default attributes like auto-reminders
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.industry})"



class BusinessAIWorker(models.Model):
    """Stores AI Worker instances for businesses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(User, on_delete=models.CASCADE)  # Business that owns the AI Worker
    ai_employer = models.ForeignKey(AIEmployer, on_delete=models.CASCADE, related_name="ai_workers")  # Link to AI Employer
    ai_worker = models.ForeignKey(AIWorker, on_delete=models.CASCADE)  # Links to AIWorker
    configurations = models.JSONField()  # Stores custom settings
    status = models.CharField(max_length=50, choices=[
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("disabled", "Disabled"),
    ], default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business}'s {self.ai_worker.name}"
    

class AITask(models.Model):
    TASK_EXECUTION_TYPES = [
        ('fully_autonomous', 'Fully Autonomous'),
        ('rule_based', 'Rule-Based'),
        ('hybrid', 'Hybrid (AI + Human Approval)'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    execution_type = models.CharField(max_length=50, choices=TASK_EXECUTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_ai_worker = models.ForeignKey('AIWorker', on_delete=models.CASCADE, related_name='tasks')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.execution_type})"



class BusinessAITaskExecution(models.Model):
    """Stores execution requests for AI Worker tasks"""
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_worker = models.ForeignKey(
        "BusinessAIWorker", on_delete=models.CASCADE, related_name="executed_tasks"
    )
    ai_task = models.ForeignKey(
        "AITask", on_delete=models.CASCADE, related_name="executions"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    execution_type = models.CharField(max_length=50, choices=[
        ("fully_autonomous", "Fully Autonomous"),
        ("rule_based", "Rule-Based"),
        ("hybrid", "Hybrid (AI + Human Approval)"),
    ])
    payload = models.JSONField(default=dict, blank=True)  # Extra data needed for execution
    requested_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(default=dict, blank=True)  # Execution results (e.g., reports, errors)

    def mark_in_progress(self):
        """Mark task as in progress and set started time"""
        self.status = "in_progress"
        self.started_at = now()
        self.save()

    def mark_completed(self, result_data=None):
        """Mark task as completed with results"""
        self.status = "completed"
        self.completed_at = now()
        self.result = result_data or {}
        self.save()

    def mark_failed(self, error_message):
        """Mark task as failed and store error message"""
        self.status = "failed"
        self.completed_at = now()
        self.result = {"error": error_message}
        self.save()

    def __str__(self):
        return f"{self.ai_task.name} for {self.business_worker.business} - {self.status}"
    

class AIWorkerLearningRecord(models.Model):
    """
    🧠 AUTONOMOUS LEARNING: Persistent storage for AI worker learning data
    
    This model enables true autonomous behavior by:
    1. Storing execution performance and outcomes
    2. Tracking strategy effectiveness over time  
    3. Building knowledge base for optimization
    4. Enabling cross-execution learning and improvement
    """
    
    EXECUTION_STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('partial', 'Partial Success'),
    ]
    
    STRATEGY_TYPES = [
        ('high_performance', 'High Performance'),
        ('balanced', 'Balanced'),
        ('rapid_processing', 'Rapid Processing'),
        ('custom', 'Custom Strategy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_worker = models.ForeignKey(
        BusinessAIWorker, 
        on_delete=models.CASCADE, 
        related_name='learning_records'
    )
    
    # Execution Details
    execution_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    execution_status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES)
    execution_time = models.FloatField(help_text="Execution time in seconds")
    
    # Context and Strategy
    file_size = models.BigIntegerField(help_text="File size in bytes")
    strategy_used = models.CharField(max_length=50, choices=STRATEGY_TYPES)
    ai_model_used = models.CharField(max_length=50, null=True, blank=True)
    processing_mode = models.CharField(max_length=50, null=True, blank=True)
    
    # Learning Data
    context_data = models.JSONField(default=dict, help_text="Full execution context")
    result_data = models.JSONField(default=dict, help_text="Execution results")
    error_details = models.TextField(null=True, blank=True)
    learning_insights = models.JSONField(default=list, help_text="Generated insights")
    
    # Performance Metrics
    properties_processed = models.IntegerField(null=True, blank=True)
    processing_rate = models.FloatField(null=True, blank=True, help_text="Properties per second")
    success_rate = models.FloatField(null=True, blank=True, help_text="Success percentage")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    business_context = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business_worker', 'execution_status']),
            models.Index(fields=['strategy_used', 'execution_time']),
            models.Index(fields=['file_size', 'processing_rate']),
        ]
    
    def __str__(self):
        return f"Learning: {self.task_name} - {self.execution_status} ({self.execution_time}s)"
    
    @property
    def efficiency_score(self):
        """Calculate efficiency score based on time and success"""
        if self.execution_status == 'success' and self.execution_time > 0:
            # Lower time = higher efficiency
            base_score = 100 / max(self.execution_time, 1)
            # Boost for processing rate
            if self.processing_rate:
                base_score *= min(self.processing_rate, 10)
            return min(round(base_score, 2), 100)
        return 0
    
    @classmethod
    def get_strategy_performance(cls, business_worker, strategy_type):
        """Get performance metrics for a specific strategy"""
        records = cls.objects.filter(
            business_worker=business_worker,
            strategy_used=strategy_type,
            execution_status='success'
        )
        
        if not records.exists():
            return None
            
        avg_time = records.aggregate(avg_time=models.Avg('execution_time'))['avg_time']
        avg_rate = records.aggregate(avg_rate=models.Avg('processing_rate'))['avg_rate']
        success_count = records.count()
        
        return {
            'average_time': round(avg_time, 2),
            'average_rate': round(avg_rate or 0, 2),
            'execution_count': success_count,
            'efficiency_score': records.aggregate(
                avg_efficiency=models.Avg('processing_rate')
            )['avg_efficiency'] or 0
        }
    

# 🏦 FINANCIAL MANAGEMENT MODELS
class Tenant(models.Model):
    """Tenant information for financial management"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.JSONField(default=dict, blank=True)
    tenant_since = models.DateField()
    payment_preferences = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tenant: {self.name}"
    
    class Meta:
        ordering = ['name']


class Lease(models.Model):
    """Lease agreements and rental terms"""
    LEASE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    property_listing = models.ForeignKey('ai_property_manager.PropertyListing', on_delete=models.CASCADE, blank=True, null=True)
    property_address = models.CharField(max_length=500)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lease_start = models.DateField()
    lease_end = models.DateField()
    rent_due_day = models.IntegerField(default=1)  # Day of month rent is due
    status = models.CharField(max_length=20, choices=LEASE_STATUS_CHOICES, default='pending')
    late_fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    late_fee_grace_days = models.IntegerField(default=5)
    lease_terms = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Lease: {self.tenant.name} - {self.property_address}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'active' and self.lease_start <= today <= self.lease_end
    
    class Meta:
        ordering = ['-lease_start']


class Payment(models.Model):
    """Payment records and transaction history"""
    PAYMENT_TYPE_CHOICES = [
        ('rent', 'Rent Payment'),
        ('late_fee', 'Late Fee'),
        ('security_deposit', 'Security Deposit'),
        ('maintenance', 'Maintenance Fee'),
        ('utility', 'Utility Payment'),
        ('other', 'Other')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('money_order', 'Money Order'),
        ('online', 'Online Payment'),
        ('other', 'Other')
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='rent')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.CharField(max_length=100, default='AI System')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment: {self.tenant.name} - ${self.amount} ({self.payment_date})"
    
    class Meta:
        ordering = ['-payment_date', '-created_at']


class LateFee(models.Model):
    """Late fee tracking and management"""
    FEE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('waived', 'Waived'),
        ('paid', 'Paid')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='late_fees')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='late_fees')
    original_payment_due = models.DateField()
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2)
    days_late = models.IntegerField()
    status = models.CharField(max_length=20, choices=FEE_STATUS_CHOICES, default='pending')
    applied_date = models.DateField(blank=True, null=True)
    waived_date = models.DateField(blank=True, null=True)
    waived_reason = models.TextField(blank=True)
    waived_by = models.CharField(max_length=100, blank=True)
    paid_date = models.DateField(blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name='late_fees_paid')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Late Fee: {self.tenant.name} - ${self.fee_amount} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']


class PaymentReminder(models.Model):
    """Payment reminder scheduling and tracking"""
    REMINDER_TYPE_CHOICES = [
        ('upcoming', 'Upcoming Payment'),
        ('due_today', 'Due Today'),
        ('overdue', 'Overdue Payment'),
        ('late_fee_notice', 'Late Fee Notice')
    ]
    
    REMINDER_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='reminders')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=REMINDER_STATUS_CHOICES, default='scheduled')
    message_content = models.TextField()
    delivery_method = models.CharField(max_length=20, default='email')
    response_received = models.BooleanField(default=False)
    response_content = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reminder: {self.tenant.name} - {self.reminder_type} ({self.status})"
    
    class Meta:
        ordering = ['-scheduled_date']


class FinancialReport(models.Model):
    """Financial reports and analytics"""
    REPORT_TYPE_CHOICES = [
        ('monthly_summary', 'Monthly Summary'),
        ('payment_status', 'Payment Status Report'),
        ('overdue_report', 'Overdue Payments Report'),
        ('late_fee_report', 'Late Fee Report'),
        ('annual_summary', 'Annual Summary'),
        ('tenant_profile', 'Tenant Financial Profile'),
        ('collection_analysis', 'Collection Analysis')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)
    report_period_start = models.DateField()
    report_period_end = models.DateField()
    generated_date = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=100, default='AI System')
    report_data = models.JSONField()  # Stores the complete report data
    summary_stats = models.JSONField(default=dict)  # Key metrics for quick access
    file_path = models.CharField(max_length=500, blank=True)  # If report exported to file
    is_automated = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Report: {self.get_report_type_display()} ({self.report_period_start} to {self.report_period_end})"
    
    class Meta:
        ordering = ['-generated_date']
