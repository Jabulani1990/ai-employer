from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ACCOUNT_TYPES = [
        ('freelancer', 'Freelancer'),
        ('business', 'Business')
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ]


    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)

    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        null=True, blank=True,
        help_text="Only applicable for freelancers"
    )

    completed_tasks = models.IntegerField(default=0)
    workload = models.IntegerField(default=0)  # Tracks active tasks assigned

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})" if self.first_name and self.last_name else self.username

    @property
    def business_profile(self):
        """Get the business profile associated with this user if they are a business owner."""
        if self.account_type == 'business':
            return self.aiemployer  # Assuming AIEmployer has a related_name='aiemployer'
        return None
    

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name="skills", blank=True)

    def __str__(self):
        return self.name

