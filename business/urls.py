from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CreateBusinessAPIView.as_view(), name='register_business_api'),
    path('ai-employer/register/', views.register_ai_employer, name='register_ai_employer'),
    path('ai-employer/list/', views.list_ai_employers, name='list_ai_employers'),
    path("ai-settings/", views.AIEmployerSettingsAPIView.as_view(), name="ai-employer-settings"),
]
