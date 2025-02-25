from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AIWorker, BusinessAIWorker
from .serializers import AIWorkerSerializer, BusinessAIWorkerSerializer
from rest_framework import generics, permissions

class AIWorkerListView(generics.ListAPIView):
    """API endpoint to list all AI Workers with filters."""
    queryset = AIWorker.objects.all()
    serializer_class = AIWorkerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['industry', 'execution_type']
    search_fields = ['job_functions']

class CreateBusinessAIWorkerView(generics.CreateAPIView):
    """API endpoint to allow businesses to spin up an AI Worker"""
    queryset = BusinessAIWorker.objects.all()
    serializer_class = BusinessAIWorkerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Ensure the AI Worker is linked to the authenticated business"""
        serializer.save(business=self.request.user)
