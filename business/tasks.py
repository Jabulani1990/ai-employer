from celery import shared_task
from business.services.matching import find_best_candidate
from business.models import Task

@shared_task
def reassign_unassigned_tasks():
    """
    Periodically checks for unassigned tasks and assigns the best available freelancer.
    """
    unassigned_tasks = Task.objects.filter(is_assigned=False)

    for task in unassigned_tasks:
        find_best_candidate = find_best_candidate(task)
        if find_best_candidate:
            task.assign_task(find_best_candidate)

    return f"{unassigned_tasks.count()} tasks processed"


@shared_task
def auto_assign_freelancers():
    """Auto-assign freelancers to unassigned tasks."""
    unassigned_tasks = Task.objects.filter(status='pending', assigned_user=None)

    for task in unassigned_tasks:
        freelancer = find_best_candidate(task)
        if freelancer:
            task.assign_task(freelancer)




@shared_task
def test_task():
    print("Celery Beat is running a scheduled task!")
    return "Task executed"
