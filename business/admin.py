from django.contrib import admin
from .models import Business, AIEmployer, Task

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'industry_type', 'created_at')

@admin.register(AIEmployer)
class AIEmployerAdmin(admin.ModelAdmin):
    list_display = ('business', 'budget', 'created_at')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'ai_employer', 'is_assigned', 'created_at')
