from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from business.utils.task_generator import AutonomousTaskGenerator

from .models import AIEmployer, Business, AIEmployerSettings,Task, TaskCategory
from .serializers import AIEmployerSerializer, BusinessSerializer, AIEmployerSettingsSerializer, TaskSerializer
from rest_framework.permissions import IsAuthenticated
from business.utils.task_categorization import categorize_task  # Import AI categorization function


class CreateBusinessAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BusinessSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['POST'])
def register_ai_employer(request):
    """
    Handle the creation of an AI Employer.
    """
    if request.method == 'POST':
        serializer = AIEmployerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_ai_employers(request):
    """
    Retrieve the list of AI Employers.
    """
    if request.method == 'GET':
        ai_employers = AIEmployer.objects.all()
        serializer = AIEmployerSerializer(ai_employers, many=True)
        return Response(serializer.data)


class AIEmployerSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve AI Employer Settings"""
        if request.user.account_type == "freelancer":
            return Response(
                {"error": "Freelancers cannot access AI employer settings."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Ensure the user has a registered business
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            return Response(
                {"error": "You must have a registered business to access this feature."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure the business has an AIEmployer instance
        ai_employer = AIEmployer.objects.filter(business=business).first()
        if not ai_employer:
            return Response(
                {"error": "You must create an AI employer before accessing settings."},
                status=status.HTTP_400_BAD_REQUEST
            )

        settings, _ = AIEmployerSettings.objects.get_or_create(business_owner=request.user)
        serializer = AIEmployerSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        """Update AI Employer Settings"""
        if request.user.account_type == "freelancer":
            return Response(
                {"error": "Freelancers cannot modify AI employer settings."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Ensure the user has a registered business
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            return Response(
                {"error": "You must have a registered business to modify settings."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure the business has an AIEmployer instance
        ai_employer = AIEmployer.objects.filter(business=business).first()
        if not ai_employer:
            return Response(
                {"error": "You must create an AI employer before modifying settings."},
                status=status.HTTP_400_BAD_REQUEST
            )

        settings, _ = AIEmployerSettings.objects.get_or_create(business_owner=request.user)
        serializer = AIEmployerSettingsSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskCategorizationView(APIView):
    """
    API endpoint to create a task and auto-categorize it using AI.
    """
    
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()

            # AI-based categorization
            category = categorize_task(task.description)

            if category:
                task.category = category
                task.save()

            return Response({
                "message": "Task created successfully",
                "task": TaskSerializer(task).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def generate_ai_tasks(request, ai_employer_id):
#     ai_employer = AIEmployer.objects.get(id=ai_employer_id)
#     task_generator = AutonomousTaskGenerator(ai_employer)
#     generated_tasks = task_generator.generate_autonomous_tasks()
    
#     return JsonResponse({
#         'tasks': generated_tasks
#     })

@api_view(['POST'])
def generate_ai_tasks(request, ai_employer_id):
    ai_employer = AIEmployer.objects.get(id=ai_employer_id)
    task_generator = AutonomousTaskGenerator(ai_employer)
    generated_tasks = task_generator.generate_autonomous_tasks()

    return JsonResponse({
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'required_skills': task.required_skills,
                'category': task.category.job_role if task.category else None,
                'goal_alignment': task.goal_alignment,
                'urgency': task.urgency,
                'budget': str(task.budget)  # Convert DecimalField to string
            }
            for task in generated_tasks
        ]
    }, safe=False)
