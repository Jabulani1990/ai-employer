from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .chatbot_tasks import process_customer_inquiry_task, process_faq_inquiry_task, process_tenant_inquiry_task
import logging
import time

logger = logging.getLogger(__name__)


def generate_fallback_response(inquiry_data):
    """
    🛡️ INTELLIGENT FALLBACK: Generate contextual response when AI processing fails
    """
    message = inquiry_data.get('message', '').lower()
    inquiry_type = inquiry_data.get('inquiry_type', 'general')
    
    # Context-aware fallback responses
    if inquiry_type == 'availability_inquiry' or 'price' in message or 'available' in message:
        return {
            "response": "I'd be happy to help you with pricing and availability! Our current rates range from $1,200-$1,800 depending on unit size and amenities. We have several units available for immediate move-in. Would you like me to connect you with our leasing specialist for detailed pricing and a tour?",
            "confidence": 0.8,
            "inquiry_type": "availability_inquiry",
            "follow_up_required": True,
            "escalation_needed": False
        }
    elif 'contact' in message or 'hours' in message or 'phone' in message:
        return {
            "response": "Here's our contact information: Phone: (555) 123-4567, Email: info@propertymanagement.com, Office Hours: Mon-Fri 9AM-6PM, Sat 10AM-2PM. How else can I assist you?",
            "confidence": 0.9,
            "inquiry_type": "contact_info",
            "follow_up_required": False,
            "escalation_needed": False
        }
    elif 'maintenance' in message or 'repair' in message or 'broken' in message:
        return {
            "response": "I can help you with your maintenance request! For urgent issues, please call our emergency line: (555) 123-HELP. For non-urgent requests, I can help you submit a work order. Could you please describe the issue you're experiencing?",
            "confidence": 0.85,
            "inquiry_type": "maintenance_request",
            "follow_up_required": True,
            "escalation_needed": 'emergency' in message or 'urgent' in message
        }
    else:
        return {
            "response": "Thank you for contacting us! I'm here to help with questions about our properties, pricing, availability, maintenance, and more. Could you tell me a bit more about what you're looking for?",
            "confidence": 0.7,
            "inquiry_type": "general_inquiry",
            "follow_up_required": True,
            "escalation_needed": False
        }


@api_view(['GET', 'POST'])
def customer_inquiry_api(request):
    """
    🤖 CUSTOMER INQUIRY API: Process customer inquiries through autonomous chatbot
    
    POST /api/ai-property-manager/chatbot/inquiry/
    GET /api/ai-property-manager/chatbot/inquiry/ (for testing)
    """
    
    # Quick test endpoint for GET requests
    if request.method == 'GET':
        return Response({
            "message": "✅ Chatbot API is working!",
            "endpoint": "customer_inquiry_api",
            "available_methods": ["GET", "POST"],
            "test_payload": {
                "message": "What are your office hours?",
                "customer_id": "test_customer",
                "inquiry_type": "faq"
            }
        }, status=status.HTTP_200_OK)
    
    try:
        # Validate required fields
        message = request.data.get('message')
        if not message:
            return Response({
                "error": "Message is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare inquiry data for autonomous processing
        inquiry_data = {
            "message": message,
            "customer_id": request.data.get('customer_id', 'anonymous'),
            "inquiry_type": request.data.get('inquiry_type', 'general'),
            "property_context": request.data.get('property_context', {}),
            "conversation_history": request.data.get('conversation_history', [])
        }
        
        # 🤖 AUTONOMOUS PROCESSING: Use the real AI chatbot
        try:
            from .ai_chatbot import AutonomousChatbotExecutor
            
            # Initialize autonomous chatbot
            chatbot = AutonomousChatbotExecutor("customer_inquiry")
            
            # Process with full autonomous intelligence
            result = chatbot.process_customer_inquiry(inquiry_data)
            
            # Add processing metadata
            result['test_mode'] = False
            result['processing_method'] = 'autonomous_ai'
            result['received_data'] = inquiry_data
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as ai_error:
            # Fallback to simple response if AI processing fails
            logger.warning(f"⚠️ AI processing failed, using fallback: {str(ai_error)}")
            
            # Intelligent fallback based on inquiry type
            fallback_response = generate_fallback_response(inquiry_data)
            
            return Response({
                **fallback_response,
                "test_mode": True,
                "processing_method": "fallback",
                "ai_error": str(ai_error),
                "received_data": inquiry_data
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Customer inquiry API error: {str(e)}")
        return Response({
            "error": "Failed to process inquiry",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """
    🤖 CUSTOMER INQUIRY API: Process customer inquiries through autonomous chatbot
    
    POST /api/ai-workers/chatbot/inquiry/
    
    Body:
    {
        "message": "I want to know about available apartments",
        "customer_id": "cust_123",
        "inquiry_type": "availability_inquiry",  // optional
        "property_context": {  // optional
            "property_id": "prop_456"
        }
    }
    
    Response:
    {
        "response": "AI generated response",
        "confidence": 0.95,
        "inquiry_type": "availability_inquiry",
        "follow_up_required": false,
        "escalation_needed": false
    }
    """
    
    try:
        # Validate required fields
        message = request.data.get('message')
        if not message:
            return Response({
                "error": "Message is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare inquiry data
        inquiry_data = {
            "message": message,
            "customer_id": request.data.get('customer_id', f'user_{request.user.id}'),
            "inquiry_type": request.data.get('inquiry_type', 'general'),
            "property_context": request.data.get('property_context', {}),
            "conversation_history": request.data.get('conversation_history', [])
        }
        
        # Process with autonomous chatbot
        task_result = process_customer_inquiry_task.delay(inquiry_data)
        result = task_result.get(timeout=30)  # 30 second timeout
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Customer inquiry API error: {str(e)}")
        return Response({
            "error": "Failed to process inquiry",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def faq_inquiry_api(request):
    """
    ❓ FAQ API: Process frequently asked questions
    
    POST /api/ai-workers/chatbot/faq/
    """
    
    try:
        faq_data = {
            "question": request.data.get('question'),
            "customer_id": request.data.get('customer_id', f'user_{request.user.id}'),
            "conversation_history": request.data.get('conversation_history', [])
        }
        
        if not faq_data["question"]:
            return Response({
                "error": "Question is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        task_result = process_faq_inquiry_task.delay(faq_data)
        result = task_result.get(timeout=30)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ FAQ API error: {str(e)}")
        return Response({
            "error": "Failed to process FAQ",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_inquiry_api(request):
    """
    🏠 TENANT INQUIRY API: Process tenant-specific inquiries
    
    POST /api/ai-workers/chatbot/tenant/
    """
    
    try:
        tenant_data = {
            "message": request.data.get('message'),
            "tenant_id": request.data.get('tenant_id', f'user_{request.user.id}'),
            "property_id": request.data.get('property_id'),
            "unit_number": request.data.get('unit_number'),
            "lease_status": request.data.get('lease_status'),
            "conversation_history": request.data.get('conversation_history', [])
        }
        
        if not tenant_data["message"]:
            return Response({
                "error": "Message is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        task_result = process_tenant_inquiry_task.delay(tenant_data)
        result = task_result.get(timeout=30)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Tenant inquiry API error: {str(e)}")
        return Response({
            "error": "Failed to process tenant inquiry",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chatbot_analytics_api(request):
    """
    📊 CHATBOT ANALYTICS: Get autonomous chatbot performance metrics
    
    GET /api/ai-workers/chatbot/analytics/
    """
    
    try:
        from ai_workers.models import AIWorkerLearningRecord, BusinessAIWorker
        
        # Get business worker
        business_worker = BusinessAIWorker.objects.filter(
            business=request.user,
            ai_worker__name="AI Property Manager",
            status="active"
        ).first()
        
        if not business_worker:
            return Response({
                "error": "No active AI Property Manager found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get chatbot learning records
        chatbot_records = AIWorkerLearningRecord.objects.filter(
            business_worker=business_worker,
            task_name__in=['customer_inquiry', 'ai_chatbot', 'batch_inquiries']
        ).order_by('-created_at')[:100]
        
        if not chatbot_records.exists():
            return Response({
                "message": "No chatbot interaction data available yet",
                "total_conversations": 0,
                "success_rate": 0,
                "average_response_time": 0,
                "top_inquiry_types": []
            })
        
        # Calculate analytics
        total_conversations = chatbot_records.count()
        successful_conversations = chatbot_records.filter(execution_status='success').count()
        success_rate = (successful_conversations / total_conversations) * 100
        
        # Average response time
        avg_response_time = chatbot_records.aggregate(
            avg_time=models.Avg('execution_time')
        )['avg_time'] or 0
        
        # Top inquiry types from context data
        inquiry_types = {}
        for record in chatbot_records:
            context = record.context_data.get('conversation_analysis', {})
            intent = context.get('primary_intent', 'unknown')
            inquiry_types[intent] = inquiry_types.get(intent, 0) + 1
        
        top_inquiry_types = sorted(inquiry_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent insights
        recent_insights = []
        for record in chatbot_records[:10]:
            if record.learning_insights:
                recent_insights.extend(record.learning_insights)
        
        return Response({
            "total_conversations": total_conversations,
            "success_rate": round(success_rate, 1),
            "average_response_time": round(avg_response_time, 2),
            "top_inquiry_types": [{"type": t[0], "count": t[1]} for t in top_inquiry_types],
            "recent_insights": list(set(recent_insights))[:10],  # Unique insights
            "last_updated": chatbot_records.first().created_at if chatbot_records.exists() else None
        })
        
    except Exception as e:
        logger.error(f"❌ Chatbot analytics error: {str(e)}")
        return Response({
            "error": "Failed to fetch analytics",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot_feedback_api(request):
    """
    📝 CHATBOT FEEDBACK: Record customer feedback for learning improvement
    
    POST /api/ai-workers/chatbot/feedback/
    
    Body:
    {
        "conversation_id": "unique_id",
        "feedback_type": "helpful|not_helpful|escalation_needed",
        "rating": 5,  // 1-5 scale
        "comments": "Optional feedback comments"
    }
    """
    
    try:
        conversation_id = request.data.get('conversation_id')
        feedback_type = request.data.get('feedback_type')
        rating = request.data.get('rating')
        
        if not conversation_id or not feedback_type:
            return Response({
                "error": "conversation_id and feedback_type are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Store feedback for learning improvement
        # This could be used to retrain the chatbot or adjust strategies
        
        feedback_data = {
            "conversation_id": conversation_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "comments": request.data.get('comments', ''),
            "timestamp": timezone.now().isoformat(),
            "user_id": request.user.id
        }
        
        # Log feedback for analysis
        logger.info(f"📝 Chatbot feedback received: {feedback_data}")
        
        return Response({
            "message": "Feedback recorded successfully",
            "feedback_id": f"fb_{int(time.time())}"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Chatbot feedback error: {str(e)}")
        return Response({
            "error": "Failed to record feedback",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
