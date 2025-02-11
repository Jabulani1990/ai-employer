from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from accounts.models import User
from business.services.matching import find_best_candidate

from django.db.models.signals import post_save
from django.dispatch import receiver
from celery import shared_task

from django.contrib.auth import get_user_model
from employer_platform import settings
from django.db.models import Count, Q

User = get_user_model()





# Business Model
class Business(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="business",
        help_text="The user who owns this business.",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    industry_type = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # New Fields
    business_goals = models.TextField(
        help_text="Describe the company's goals and long-term vision.",
        null=True, blank=True
    )
    daily_operations = models.JSONField(
        help_text="List of daily business operations and responsibilities.",
        null=True, blank=True
    )


    def __str__(self):
        return self.name


# AI Employer Model
class AIEmployer(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True)  # AI employer name
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='ai_employer')
    budget = models.DecimalField(max_digits=12, decimal_places=2)  # e.g., $10,000
    job_preferences = models.TextField(help_text="Define job types or skills (e.g., Data Entry, Marketing).")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields:
    ai_employer_type = models.CharField(max_length=100, choices=[('freelancer', 'Freelancer'), ('company', 'Company')], default='company')
    location = models.CharField(max_length=255, null=True, blank=True)
    industry_category = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended')], default='active')
    joining_date = models.DateTimeField(default=now)

        # New Fields
    past_tasks = models.JSONField(
        help_text="AI memory of previously generated and completed tasks.",
        null=True, blank=True
    )
    task_generation_mode = models.CharField(
        max_length=50,
        choices=[('manual', 'Manual'), ('semi_automatic', 'Semi-Automatic'), ('fully_automatic', 'Fully Automatic')],
        default='semi_automatic',
        help_text="How aggressively AI should generate tasks."
    )
    priority_focus = models.CharField(
        max_length=255,
        help_text="Which business goal should AI prioritize? (e.g., Marketing, Sales, Customer Support)",
        null=True, blank=True
    )

    def get_ai_workers(self):
        """Fetch all AI Workers linked to this AI Employer"""
        return self.ai_workers.all()

    def save(self, *args, **kwargs):
        """ Auto-generate name if not provided """
        if not self.name:
            self.name = f"AI Employer - {slugify(self.business.name)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"AI Employer for {self.business.name}"
    
class TaskCategory(models.Model):
    INDUSTRY_CHOICES = [
        ('tech', 'Technology'), ('finance', 'Finance'), ('healthcare', 'Healthcare'), ('marketing', 'Marketing'), ('other', 'Other')
    ]
    JOB_ROLE_CHOICES = [
        ('data_entry', 'Data Entry'), ('design', 'Design'), ('writing', 'Writing'), ('development', 'Development'), ('other', 'Other')
    ]
    COMPLEXITY_CHOICES = [
        ('simple', 'Simple'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')
    ]

    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    job_role = models.CharField(max_length=50, choices=JOB_ROLE_CHOICES)
    complexity = models.CharField(max_length=50, choices=COMPLEXITY_CHOICES)

    def __str__(self):
        return f"{self.get_industry_display()} - {self.get_job_role_display()} - {self.get_complexity_display()}"


# Task Model
class Task(models.Model):
    ai_employer = models.ForeignKey(AIEmployer, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.CharField(max_length=255, help_text="Comma-separated skills required (e.g., Python, Excel).")
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    #payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    budget = models.FloatField(default=0.00)
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('completed', 'Completed')],
        default='pending'
    )
    is_assigned = models.BooleanField(default=False)
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    # New Fields
    goal_alignment = models.CharField(
        max_length=255,
        help_text="Which business goal does this task support?",
        null=True, blank=True
    )
    urgency = models.IntegerField(
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        default=2,
        help_text="How urgent is this task?"
    )

    def __str__(self):
        return f"{self.title} - {self.status}"

    def assign_task(self, user):
        """ Assign task to a user and update status """
        self.assigned_user = user
        self.status = 'assigned'
        self.is_assigned = True
        self.save()

    def auto_assign(self):
        """ AI automatically assigns the best freelancer to this task. """
        best_candidate = find_best_candidate(self)
        if best_candidate:
            self.assign_task(best_candidate)


@receiver(post_save, sender=Task)
def auto_assign_task(sender, instance, created, **kwargs):
    """Real-time assignment when a task is created."""
    if created and not instance.assigned_user:
        best_candidate = find_best_candidate(instance)
        if best_candidate:
            instance.assigned_user = best_candidate
            instance.status = 'assigned'
            instance.save()

@shared_task
def assign_unassigned_tasks():
    """Periodic AI task assignment for unassigned tasks."""
    unassigned_tasks = Task.objects.filter(status='pending', assigned_user__isnull=True)
    
    for task in unassigned_tasks:
        best_candidate = find_best_candidate(task)
        if best_candidate:
            task.assigned_user = best_candidate
            task.status = 'assigned'
            task.save()
    

class AIEmployerSettings(models.Model):
    business_owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ai_settings")
    
    # Auto-assignment toggle
    auto_assign = models.BooleanField(default=True)  # Default: AI assigns freelancers
    
    # AI Suggestion Override
    allow_override = models.BooleanField(default=True)  # Default: Business owner can override AI
    
    # Optional Customization: Matching Preferences
    prioritize_low_cost = models.BooleanField(default=False)
    prioritize_fast_response = models.BooleanField(default=False)
    prioritize_experience = models.BooleanField(default=True)  # Default: Experience is valued

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_owner.username} - AI Settings"

