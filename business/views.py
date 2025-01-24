from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import AIEmployer, Business
from .serializers import AIEmployerSerializer, BusinessSerializer

class CreateBusinessAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BusinessSerializer(data=request.data)
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

