import os
from celery import Celery

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employer_platform.settings")

celery_app = Celery("employer_platform")

# Load configuration from Django settings
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
celery_app.autodiscover_tasks()
