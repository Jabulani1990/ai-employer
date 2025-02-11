import logging
from django.utils.timezone import now
from .models import BusinessAITaskExecution, BusinessAIWorker
from .tasks import execute_ai_task  # We will define this later

logger = logging.getLogger(__name__)

def get_active_ai_workers():
    """Fetch all active AI Workers."""
    return BusinessAIWorker.objects.filter(status="active")

def get_pending_task_requests(worker):
    """Fetch pending execution requests for a given AI Worker."""
    return BusinessAITaskExecution.objects.filter(
        business_worker=worker, status="pending"
    ).order_by("-requested_at")

def process_ai_worker_tasks():
    """Main function to process AI Worker task requests."""
    active_workers = get_active_ai_workers()
    
    for worker in active_workers:
        pending_tasks = get_pending_task_requests(worker)

        for task_execution in pending_tasks:
            logger.info(f"Processing Task '{task_execution.ai_task.name}' for {worker.business}")

            # Mark task as in progress
            task_execution.mark_in_progress()

            # Dispatch the task execution asynchronously
            execute_ai_task.delay(task_execution.id)  # This will be handled in Celery

def run_task_execution_engine():
    """
    Periodically called (via Celery Beat or Cron Job)
    to check for new task execution requests.
    """
    logger.info("Starting AI Task Execution Engine...")
    process_ai_worker_tasks()
    logger.info("AI Task Execution Engine completed execution.")
