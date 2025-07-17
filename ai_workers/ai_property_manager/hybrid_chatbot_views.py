"""
🔄 HYBRID CHATBOT VIEWS: Support both original and LangGraph implementations

This allows you to:
1. Keep using your existing chatbot
2. Test the new LangGraph version
3. Switch between them easily
4. Compare performance

"""

import asyncio
import logging
import time
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

# Your existing chatbot
from .ai_chatbot import AutonomousChatbotExecutor

# New LangGraph chatbot (optional)
try:
    from .langgraph_chatbot import HybridLangGraphChatbot, LangGraphConfig, LANGGRAPH_AVAILABLE
    # Use the actual availability from the langgraph_chatbot module
    if not LANGGRAPH_AVAILABLE:
        # LangGraph dependencies not installed
        class LangGraphConfig:
            def __init__(self, **kwargs):
                raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
        
        class HybridLangGraphChatbot:
            def __init__(self, **kwargs):
                raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
        
        print("⚠️ LangGraph dependencies not installed. Run: pip install langgraph langchain langchain-openai")
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create dummy classes to prevent errors
    class LangGraphConfig:
        def __init__(self, **kwargs):
            raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
    
    class HybridLangGraphChatbot:
        def __init__(self, **kwargs):
            raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
    
    print("⚠️ LangGraph chatbot module not available. Install dependencies to enable.")

logger = logging.getLogger(__name__)


class HybridChatbotView(View):
    """
    🎯 HYBRID CHATBOT VIEW: Switch between implementations
    
    Supports:
    - Original autonomous chatbot (always available)
    - LangGraph enhanced chatbot (if dependencies installed)
    - A/B testing between implementations
    - Performance comparison
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        Handle chatbot inquiries with implementation selection
        
        POST data can include:
        {
            "message": "Customer message",
            "customer_id": "unique_id", 
            "chatbot_type": "original|langgraph|auto",
            "inquiry_type": "faq|tenant_inquiry|general",
            "property_context": {"property_id": "xxx"} (optional),
            "conversation_history": [] (optional)
        }
        """
        try:
            # Parse request data
            data = json.loads(request.body)
            
            # Determine which chatbot to use
            chatbot_type = data.get('chatbot_type', 'auto')
            
            # Handle LangGraph request when not available
            if chatbot_type == 'langgraph' and not LANGGRAPH_AVAILABLE:
                return JsonResponse({
                    'error': 'LangGraph not available',
                    'message': 'Install dependencies: pip install langgraph langchain langchain-openai',
                    'chatbot_used': 'none',
                    'langgraph_available': False,
                    'recommendation': 'Use chatbot_type: "original" or install LangGraph dependencies'
                }, status=400)
            
            # Process with appropriate chatbot
            if chatbot_type == 'langgraph' and LANGGRAPH_AVAILABLE:
                try:
                    response = asyncio.run(self._process_with_langgraph(data))
                    response['chatbot_used'] = 'langgraph'
                except ImportError as e:
                    # LangGraph import failed
                    return JsonResponse({
                        'error': 'LangGraph unavailable',
                        'message': str(e),
                        'chatbot_used': 'none',
                        'langgraph_available': False,
                        'recommendation': 'Install LangGraph dependencies or use original chatbot'
                    }, status=400)
            elif chatbot_type == 'original':
                response = self._process_with_original(data)
                response['chatbot_used'] = 'original'
            else:  # auto selection
                response = self._process_with_auto_selection(data)
            
            # Add performance metadata
            response['langgraph_available'] = LANGGRAPH_AVAILABLE
            response['timestamp'] = data.get('timestamp')
            
            return JsonResponse(response)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body',
                'chatbot_used': 'none'
            }, status=400)
            
        except Exception as e:
            logger.error(f"❌ Chatbot processing failed: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e),
                'chatbot_used': 'error_fallback'
            }, status=500)
    
    async def _process_with_langgraph(self, data: Dict) -> Dict:
        """🚀 Process with LangGraph enhanced chatbot"""
        
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph not available. Install with: pip install langgraph langchain langchain-openai")
        
        try:
            # Configure LangGraph chatbot
            config = LangGraphConfig(
                llm_model=data.get('llm_model', 'gpt-4'),
                confidence_threshold=data.get('confidence_threshold', 0.7),
                enable_learning=True
            )
            
            # Initialize and process
            chatbot = HybridLangGraphChatbot(config=config)
            response = await chatbot.process_customer_inquiry(data)
            
            # Add LangGraph specific metadata
            response['workflow_metrics'] = response.get('execution_metrics', {})
            response['autonomous_learning'] = True
            response['langgraph_enhanced'] = True
            
            print(f"✅ LangGraph processing completed: {response.get('confidence', 0):.2f} confidence")
            return response
            
        except Exception as e:
            print(f"❌ LangGraph processing failed: {str(e)}")
            raise
    
    def _process_with_original(self, data: Dict) -> Dict:
        """🤖 Process with original autonomous chatbot"""
        
        # Initialize your existing chatbot
        chatbot = AutonomousChatbotExecutor()
        response = chatbot.process_customer_inquiry(data)
        
        # Add original chatbot metadata
        response['autonomous_learning'] = True
        response['langgraph_enhanced'] = False
        
        print(f"✅ Original chatbot processing completed: {response.get('confidence', 0):.2f} confidence")
        return response
    
    def _process_with_auto_selection(self, data: Dict) -> Dict:
        """🎯 Auto-select best chatbot based on inquiry"""
        
        # Simple heuristics for auto-selection
        message = data.get('message', '').lower()
        
        # Use LangGraph for complex conversations if available
        use_langgraph = (
            LANGGRAPH_AVAILABLE and
            (
                len(data.get('conversation_history', [])) > 3 or  # Long conversation
                len(message.split()) > 20 or  # Complex message
                any(word in message for word in ['complex', 'detailed', 'explain', 'help me understand'])
            )
        )
        
        if use_langgraph:
            try:
                response = asyncio.run(self._process_with_langgraph(data))
                response['chatbot_used'] = 'langgraph (auto-selected)'
                response['selection_reason'] = 'Complex conversation detected'
            except (ImportError, Exception) as e:
                # Fallback to original if LangGraph fails
                print(f"⚠️ LangGraph auto-selection failed, falling back to original: {str(e)}")
                response = self._process_with_original(data)
                response['chatbot_used'] = 'original (langgraph-fallback)'
                response['selection_reason'] = 'LangGraph failed, using original chatbot'
                response['langgraph_error'] = str(e)
        else:
            response = self._process_with_original(data)
            response['chatbot_used'] = 'original (auto-selected)'
            response['selection_reason'] = 'Standard inquiry processing'
        
        return response


@csrf_exempt
@require_http_methods(["POST"])
def customer_inquiry_api(request):
    """
    🎯 MAIN API ENDPOINT: Customer inquiry processing
    
    This maintains your existing API while adding LangGraph support
    """
    view = HybridChatbotView()
    return view.post(request)


@csrf_exempt
@require_http_methods(["POST"])
def compare_chatbots_api(request):
    """
    🔄 COMPARISON API: Test both chatbots simultaneously
    
    Useful for A/B testing and performance comparison
    """
    try:
        data = json.loads(request.body)
        
        # Process with original chatbot
        original_start = time.time()
        original_chatbot = AutonomousChatbotExecutor()
        original_response = original_chatbot.process_customer_inquiry(data)
        original_time = time.time() - original_start
        
        comparison_result = {
            'original': {
                'response': original_response,
                'processing_time': original_time,
                'available': True
            }
        }
        
        # Process with LangGraph if available
        if LANGGRAPH_AVAILABLE:
            try:
                langgraph_start = time.time()
                
                config = LangGraphConfig(confidence_threshold=0.7)
                langgraph_chatbot = HybridLangGraphChatbot(config=config)
                langgraph_response = asyncio.run(langgraph_chatbot.process_customer_inquiry(data))
                langgraph_time = time.time() - langgraph_start
                
                comparison_result['langgraph'] = {
                    'response': langgraph_response,
                    'processing_time': langgraph_time,
                    'available': True
                }
                
                # Add comparison metrics
                comparison_result['comparison'] = {
                    'confidence_difference': langgraph_response.get('confidence', 0) - original_response.get('confidence', 0),
                    'time_difference': langgraph_time - original_time,
                    'both_escalated': original_response.get('escalation_needed', False) and langgraph_response.get('escalation_needed', False),
                    'recommendation': 'langgraph' if langgraph_response.get('confidence', 0) > original_response.get('confidence', 0) else 'original'
                }
                
            except Exception as e:
                comparison_result['langgraph'] = {
                    'error': str(e),
                    'available': False
                }
        else:
            comparison_result['langgraph'] = {
                'error': 'LangGraph dependencies not installed',
                'available': False
            }
        
        return JsonResponse(comparison_result)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Comparison failed',
            'message': str(e)
        }, status=500)


@csrf_exempt  
@require_http_methods(["GET"])
def chatbot_status_api(request):
    """
    📊 STATUS API: Check which chatbots are available
    """
    
    # Test original chatbot
    try:
        original_chatbot = AutonomousChatbotExecutor()
        original_available = True
        original_error = None
    except Exception as e:
        original_available = False
        original_error = str(e)
    
    # Test LangGraph chatbot
    langgraph_available = LANGGRAPH_AVAILABLE
    langgraph_error = None
    
    if LANGGRAPH_AVAILABLE:
        try:
            # Try to create config to test if everything works
            config = LangGraphConfig()
            langgraph_error = None
        except Exception as e:
            langgraph_available = False
            langgraph_error = f"LangGraph configuration error: {str(e)}"
    else:
        langgraph_error = "LangGraph not available. Install with: pip install langgraph langchain langchain-openai"
    
    status = {
        'chatbots': {
            'original': {
                'available': original_available,
                'error': original_error,
                'features': [
                    'Autonomous learning',
                    'Business context integration', 
                    'Real-time property data',
                    'Performance tracking'
                ]
            },
            'langgraph': {
                'available': langgraph_available,
                'error': langgraph_error,
                'features': [
                    'Advanced conversation flow',
                    'State management',
                    'LLM enhancement',
                    'Visual workflow debugging',
                    'Multi-agent coordination',
                    'All original features'
                ] if langgraph_available else []
            }
        },
        'recommendation': {
            'simple_inquiries': 'original',
            'complex_conversations': 'langgraph' if langgraph_available else 'original',
            'high_volume': 'original',
            'development_testing': 'langgraph' if langgraph_available else 'original'
        },
        'installation_guide': {
            'langgraph': 'pip install langgraph langchain langchain-openai',
            'environment_setup': 'Set OPENAI_API_KEY environment variable for LLM features'
        }
    }
    
    return JsonResponse(status)


# Keep your existing view for backward compatibility
@csrf_exempt
@require_http_methods(["POST"])
def original_customer_inquiry_api(request):
    """
    🤖 ORIGINAL API: Your existing chatbot (preserved)
    """
    try:
        data = json.loads(request.body)
        
        # Initialize your existing autonomous chatbot
        chatbot_executor = AutonomousChatbotExecutor()
        
        # Process the inquiry
        response_data = chatbot_executor.process_customer_inquiry(data)
        
        # Add API metadata
        response_data['api_version'] = 'original'
        response_data['timestamp'] = data.get('timestamp')
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
        
    except Exception as e:
        logger.error(f"❌ Original chatbot API error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to process inquiry',
            'details': str(e)
        }, status=500)
