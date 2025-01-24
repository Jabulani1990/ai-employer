from django.db import models
from django.utils.timezone import now

# Business Model
class Business(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    industry_type = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# AI Employer Model
class AIEmployer(models.Model):
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

    def __str__(self):
        return f"AI Employer for {self.business.name}"


# Task Model
class Task(models.Model):
    ai_employer = models.ForeignKey(AIEmployer, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.CharField(max_length=255, help_text="Comma-separated skills required (e.g., Python, Excel).")
    created_at = models.DateTimeField(auto_now_add=True)
    is_assigned = models.BooleanField(default=False)

    def __str__(self):
        return self.title
