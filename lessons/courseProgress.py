from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Module, CourseProgress

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_module_complete(request, course_id, module_id):
    """
    Marks the specified module as completed by the student.
    """
    try:
        course = Course.objects.get(id=course_id)
        module = course.modules.get(id=module_id)
        student = request.user

        # Ensure the student is enrolled in the course
        if not course.students.filter(id=student.id).exists():
            return Response({"error": "Você não está inscrito neste curso."}, status=status.HTTP_403_FORBIDDEN)

        # Get or create progress record for the student
        progress, created = CourseProgress.objects.get_or_create(student=student, course=course)

        # Add the module to the completed modules
        progress.completed_modules.add(module)

        return Response({"success": "Módulo marcado como completo."}, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Curso não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Module.DoesNotExist:
        return Response({"error": "Módulo não encontrado."}, status=status.HTTP_404_NOT_FOUND)
