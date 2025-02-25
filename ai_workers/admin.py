from django.contrib import admin
from .models import AIWorker, BusinessAIWorker, AITask, BusinessAITaskExecution

@admin.register(AIWorker)
class AIWorkerAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "execution_type", "created_at")
    search_fields = ("name", "industry")
    list_filter = ("execution_type",)

@admin.register(BusinessAIWorker)
class BusinessAIWorkerAdmin(admin.ModelAdmin):
    list_display = ("business", "ai_worker", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("business__username", "ai_worker__name")

@admin.register(AITask)
class AITaskAdmin(admin.ModelAdmin):
    list_display = ("name", "execution_type", "status", "priority", "created_at")
    list_filter = ("execution_type", "status", "priority")
    search_fields = ("name", "description")

@admin.register(BusinessAITaskExecution)
class BusinessAITaskExecutionAdmin(admin.ModelAdmin):
    list_display = ("business_worker", "ai_task", "status", "requested_at", "completed_at")
    list_filter = ("status",)
    search_fields = ("business_worker__business__username", "ai_task__name")

