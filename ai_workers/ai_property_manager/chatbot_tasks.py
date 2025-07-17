from celery import shared_task
from .ai_chatbot import AutonomousChatbotExecutor
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_customer_inquiry_task(inquiry_data):
    """
    🤖 AUTONOMOUS CUSTOMER SERVICE: Intelligent inquiry processing
    
    AUTONOMOUS FEATURES:
    - ✅ Context-aware response generation
    - ✅ Learning from conversation patterns  
    - ✅ Adaptive strategy selection
    - ✅ Automatic escalation detection
    - ✅ Continuous improvement through feedback
    
    Args:
        inquiry_data: {
            "message": "Customer message",
            "customer_id": "unique_id", 
            "inquiry_type": "faq|tenant_inquiry|general",
            "property_context": {"property_id": "xxx"} (optional),
            "conversation_history": [] (optional)
        }
    
    Returns:
        {
            "response": "AI generated response",
            "confidence": 0.95,
            "inquiry_type": "detected_type",
            "follow_up_required": False,
            "escalation_needed": False
        }
    """
    
    # Initialize autonomous chatbot executor
    chatbot = AutonomousChatbotExecutor("customer_inquiry")
    
    print(f"🤖 Processing customer inquiry: {inquiry_data.get('inquiry_type', 'general')}")
    
    try:
        # Execute with autonomous intelligence
        result = chatbot.process_customer_inquiry(inquiry_data)
        
        print(f"💬 Response generated with {result['confidence']:.1%} confidence")
        print(f"🎯 Detected intent: {result['inquiry_type']}")
        
        if result.get('escalation_needed'):
            print(f"⬆️ Escalation recommended")
            # TODO: Trigger escalation workflow
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Chatbot processing failed: {str(e)}")
        
        # Return fallback response
        return {
            "response": "I apologize for the technical difficulty. Please contact our office directly for assistance.",
            "confidence": 0.1,
            "inquiry_type": "system_error",
            "follow_up_required": True,
            "escalation_needed": True,
            "error": str(e)
        }


@shared_task
def process_faq_inquiry_task(faq_data):
    """
    ❓ FAQ PROCESSING: Autonomous FAQ handling
    
    Handles common questions with learned response optimization
    """
    
    # Convert FAQ to standard inquiry format
    inquiry_data = {
        "message": faq_data.get("question", ""),
        "customer_id": faq_data.get("customer_id", "anonymous"),
        "inquiry_type": "faq",
        "conversation_history": faq_data.get("conversation_history", [])
    }
    
    # Use main chatbot processor
    return process_customer_inquiry_task.delay(inquiry_data)


@shared_task
def process_tenant_inquiry_task(tenant_data):
    """
    🏠 TENANT INQUIRY PROCESSING: Autonomous tenant service
    
    Handles tenant-specific inquiries with property context
    """
    
    # Convert tenant inquiry to standard format
    inquiry_data = {
        "message": tenant_data.get("message", ""),
        "customer_id": tenant_data.get("tenant_id", "unknown"),
        "inquiry_type": "tenant_inquiry",
        "property_context": {
            "property_id": tenant_data.get("property_id"),
            "unit_number": tenant_data.get("unit_number"),
            "lease_status": tenant_data.get("lease_status")
        },
        "conversation_history": tenant_data.get("conversation_history", [])
    }
    
    # Use main chatbot processor with tenant context
    return process_customer_inquiry_task.delay(inquiry_data)


@shared_task
def batch_process_inquiries_task(inquiries_list):
    """
    📊 BATCH PROCESSING: Handle multiple inquiries efficiently
    
    Autonomous batch processing with load balancing and optimization
    """
    
    results = []
    chatbot = AutonomousChatbotExecutor("batch_inquiries")
    
    print(f"🔄 Processing {len(inquiries_list)} inquiries in batch")
    
    for inquiry in inquiries_list:
        try:
            result = chatbot.process_customer_inquiry(inquiry)
            results.append({
                "inquiry_id": inquiry.get("id"),
                "success": True,
                "result": result
            })
        except Exception as e:
            results.append({
                "inquiry_id": inquiry.get("id"),
                "success": False,
                "error": str(e)
            })
    
    success_rate = sum(1 for r in results if r["success"]) / len(results) * 100
    print(f"📈 Batch completed: {success_rate:.1f}% success rate")
    
    return {
        "total_processed": len(inquiries_list),
        "success_rate": success_rate,
        "results": results
    }
