from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from lessons.models import Course, CourseProgress, Content, Module
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_content_complete(request, course_id, content_id):
    """
    Marks the specified content as completed by the student.
    """
    try:
        course = Course.objects.get(id=course_id)
        content = Content.objects.get(id=content_id)
        student = request.user
        
        # Ensure the student is enrolled in the course
        if not course.students.filter(id=student.id).exists():
            return Response({"error": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

        # Get or create progress record for the student
        progress, created = CourseProgress.objects.get_or_create(student=student, course=course)

        # Add the content to the completed contents
        progress.completed_contents.add(content)

        return Response({"success": "Content marked as complete."}, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    except Content.DoesNotExist:
        return Response({"error": "Content not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
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
            return Response({"error": "You are not enrolled in this course."}, status=status.HTTP_403_FORBIDDEN)

        # Get or create progress record for the student
        progress, created = CourseProgress.objects.get_or_create(student=student, course=course)

        # Add the module to the completed modules
        progress.completed_modules.add(module)

        return Response({"success": "Module marked as complete."}, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    except Module.DoesNotExist:
        return Response({"error": "Module not found."}, status=status.HTTP_404_NOT_FOUND)
