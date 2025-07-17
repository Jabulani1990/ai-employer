from django.urls import path
from .chatbot_views import (
    customer_inquiry_api,
    faq_inquiry_api,
    tenant_inquiry_api,
    chatbot_analytics_api,
    chatbot_feedback_api
)

# Import hybrid chatbot views
from .hybrid_chatbot_views import (
    customer_inquiry_api as hybrid_inquiry_api,
    compare_chatbots_api,
    chatbot_status_api,
    original_customer_inquiry_api
)

# 🤖 AUTONOMOUS AI CHATBOT URLS
# These endpoints enable businesses to integrate autonomous customer service
# Now supports both original and LangGraph implementations

urlpatterns = [
    # 🚀 HYBRID CHATBOT ENDPOINTS (New - supports both implementations)
    path('inquiry/', hybrid_inquiry_api, name='hybrid_customer_inquiry'),  # Main endpoint
    path('compare/', compare_chatbots_api, name='compare_chatbots'),  # A/B testing
    path('status/', chatbot_status_api, name='chatbot_status'),  # Check availability
    
    # 🤖 ORIGINAL CHATBOT ENDPOINTS (Preserved for backward compatibility)
    path('original/inquiry/', original_customer_inquiry_api, name='original_customer_inquiry'),
    path('faq/', faq_inquiry_api, name='faq_inquiry'),
    path('tenant/', tenant_inquiry_api, name='tenant_inquiry'),
    
    # Analytics and feedback
    path('analytics/', chatbot_analytics_api, name='chatbot_analytics'),
    path('feedback/', chatbot_feedback_api, name='chatbot_feedback'),
]
