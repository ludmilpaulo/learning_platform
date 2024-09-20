from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Course, CourseProgress

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_students_progress(request, course_id):
    """
    Retrieve all students' progress in a course.
    """
    try:
        # Fetch the course by ID
        course = get_object_or_404(Course, id=course_id)
        
        # Ensure the user is the owner of the course
        if course.owner != request.user:
            return Response({"error": "Você não tem permissão para acessar esse curso."}, status=status.HTTP_403_FORBIDDEN)

        # Get the students' progress in the course
        progress_data = course.get_students_progress()

        return Response(progress_data, status=status.HTTP_200_OK)
    
    except Course.DoesNotExist:
        return Response({"error": "Curso não encontrado."}, status=status.HTTP_404_NOT_FOUND)
