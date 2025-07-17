from django.urls import path, include
from .views import AIWorkerListView, CreateBusinessAIWorkerView

urlpatterns = [
    path("ai-workers/", AIWorkerListView.as_view(), name="ai-worker-list"),
    path("business-ai-workers/", CreateBusinessAIWorkerView.as_view(), name="create-business-ai-worker"),
    
    # 🏦 Financial Management API
    path("financial/", include('ai_workers.ai_property_manager.services.financial_management.urls')),
]
