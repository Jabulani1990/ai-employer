import logging
from celery import shared_task
from django.utils.timezone import now
from .models import BusinessAITaskExecution

logger = logging.getLogger(__name__)

@shared_task
def execute_ai_task(task_id):
    """
    Executes a specific AI Task requested by a Business AI Worker.
    """
    try:
        # Fetch the task execution request
        task_execution = BusinessAITaskExecution.objects.get(id=task_id)
        logger.info(f"Executing Task: {task_execution.ai_task.name} for {task_execution.business_worker.business}")

        # Determine execution type
        if task_execution.execution_type == "fully_autonomous":
            result = handle_fully_autonomous_task(task_execution)
        elif task_execution.execution_type == "rule_based":
            result = handle_rule_based_task(task_execution)
        elif task_execution.execution_type == "hybrid":
            result = handle_hybrid_task(task_execution)
        else:
            raise ValueError("Unknown execution type")

        # Mark task as completed with the result
        task_execution.mark_completed(result)
        logger.info(f"Task '{task_execution.ai_task.name}' completed successfully.")

    except BusinessAITaskExecution.DoesNotExist:
        logger.error(f"Task execution ID {task_id} not found.")
    except Exception as e:
        logger.error(f"Error executing task ID {task_id}: {str(e)}")
        task_execution.mark_failed(str(e))



def handle_rule_based_task(task_execution):
    """
    Handles AI task execution in rule-based mode.
    """
    rules = task_execution.payload.get("rules", {})
    
    # Example rule: If property value < X, don't proceed
    if rules.get("property_value") and rules["property_value"] < 50000:
        return {"status": "Skipped due to low property value"}

    # Execute AI task based on the rules
    return handle_fully_autonomous_task(task_execution)


def handle_hybrid_task(task_execution):
    """
    Handles AI task execution in hybrid mode (AI + Human Approval).
    """
    # Simulating AI processing
    ai_result = handle_fully_autonomous_task(task_execution)

    # Mark task as awaiting human approval
    return {"status": "Awaiting human review", "ai_result": ai_result}

def handle_fully_autonomous_task(task_execution):
    """
    Handles AI task execution in fully autonomous mode.
    """
    # AI Worker should process the task based on the AITask assigned
    task_name = task_execution.ai_task.name

    # Simulating AI execution (replace with actual AI processing logic)
    if task_name == "Generate Property Report":
        result = {"report": f"Generated AI report for {task_execution.payload.get('property_id')}"}
    elif task_name == "Analyze Market Trends":
        result = {"analysis": "AI Market Analysis Data"}
    else:
        result = {"info": f"Executed {task_name} successfully"}

    return result
