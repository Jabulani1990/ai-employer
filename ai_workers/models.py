import uuid
from django.db import models
from django.contrib.auth import get_user_model
from business.models import AIEmployer
import uuid
from django.utils.timezone import now

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
