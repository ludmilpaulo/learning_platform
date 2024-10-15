from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Course, CourseProgress


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_students_progress(request, course_id):
    """
    Retrieve all students' progress in a course.
    """
    try:
        course = get_object_or_404(Course, id=course_id)

        if course.owner != request.user:
            return Response(
                {"error": "Você não tem permissão para acessar esse curso."},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress_data = course.get_students_progress()

        return Response(progress_data, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response(
            {"error": "Curso não encontrado."}, status=status.HTTP_404_NOT_FOUND
        )


import logging

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def activate_student(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)

    # Ensure the user is the owner of the course
    if course.owner != request.user:
        return Response(
            {"error": "Você não tem permissão para acessar esse curso."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        # Try to get the student's progress, create it if it doesn't exist
        progress, created = CourseProgress.objects.get_or_create(
            course=course, student_id=student_id
        )

        # If progress is newly created, activate the student
        progress.is_active = True
        progress.save()

        if created:
            return Response(
                {
                    "success": "Estudante foi ativado com sucesso e registro de progresso foi criado."
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"success": "Estudante ativado com sucesso."}, status=status.HTTP_200_OK
            )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def deactivate_student(request, course_id, student_id):
    """
    Deactivate a student's access to the course.
    """
    course = get_object_or_404(Course, id=course_id)

    # Ensure the user is the owner of the course
    if course.owner != request.user:
        return Response(
            {"error": "Você não tem permissão para acessar esse curso."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        progress = CourseProgress.objects.get(course=course, student_id=student_id)
        progress.is_active = False
        progress.save()
        return Response(
            {"success": "Estudante desativado com sucesso."}, status=status.HTTP_200_OK
        )
    except CourseProgress.DoesNotExist:
        return Response(
            {"error": "Progresso do estudante não encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )
