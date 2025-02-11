from django.db.models.signals import post_save
from django.dispatch import receiver
from business.models import Task
from utils.task_categorization import categorize_task

@receiver(post_save, sender=Task)
def auto_categorize_task(sender, instance, created, **kwargs):
    """ Automatically categorizes a task when it's created """
    if created and not instance.category:
        category = categorize_task(instance.description)
        if category:
            instance.category = category
            instance.save()
