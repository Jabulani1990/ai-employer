from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CreateBusinessAPIView.as_view(), name='register_business_api'),
    path('ai-employer/register/', views.register_ai_employer, name='register_ai_employer'),
    path('ai-employer/list/', views.list_ai_employers, name='list_ai_employers'),
    path("ai-settings/", views.AIEmployerSettingsAPIView.as_view(), name="ai-employer-settings"),
    path('categorize-task/', views.TaskCategorizationView.as_view(), name='categorize-task'), #Create task Manually by Business
    path('generate-tasks/<int:ai_employer_id>/', views.generate_ai_tasks, name='generate_ai_tasks')
]
