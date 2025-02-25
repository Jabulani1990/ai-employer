from django.urls import path
from .views import AIWorkerListView, CreateBusinessAIWorkerView

urlpatterns = [
    path("ai-workers/", AIWorkerListView.as_view(), name="ai-worker-list"),
    path("business-ai-workers/", CreateBusinessAIWorkerView.as_view(), name="create-business-ai-worker"),
]
