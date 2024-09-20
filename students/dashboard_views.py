from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from lessons.models import Course, CourseProgress
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import CourseSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def student_dashboard(request):
    data = request.data
    
    # Try to fetch the token from the request body
    try:
        token_key = data["token"]
        user = Token.objects.get(key=token_key).user
    except (KeyError, Token.DoesNotExist):
        return Response({"status": "failed", "error": "Invalid or missing access token."}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get all the courses the user is enrolled in
    enrolled_courses = Course.objects.filter(students=user)
    
    # Serialize the courses with their modules and contents
    serializer = CourseSerializer(enrolled_courses, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
