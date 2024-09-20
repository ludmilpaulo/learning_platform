from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Course, Module
from rest_framework.authtoken.models import Token
from .serializers import ModuleSerializer
from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated users, but we'll manually authenticate
def add_module_to_course(request, course_id):
    # Try to fetch the token from the request headers
    token_key = request.headers.get("Authorization", "").replace("Token ", "")
    
    # Validate token
    try:
        user = Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return Response({"status": "failed", "error": "Invalid or missing access token."}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Fetch the course to which the module is being added
    try:
        course = Course.objects.get(id=course_id)
    except ObjectDoesNotExist:
        return Response({"status": "failed", "error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Ensure the user adding the module is the course owner
    if course.owner != user:
        return Response({"status": "failed", "error": "You are not authorized to add a module to this course."}, status=status.HTTP_403_FORBIDDEN)
    
    # Create a new module using the request data
    serializer = ModuleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
