from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from lessons.models import Course, CourseProgress
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import CourseSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def student_dashboard(request):
    data = request.data

    # Try to fetch the token from the request body
    try:
        token_key = data.get("token", None)
        if not token_key:
            return Response(
                {"status": "failed", "error": "Missing access token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return Response(
            {"status": "failed", "error": "Invalid access token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Check if the student is active in any course
    course_progresses = CourseProgress.objects.filter(student=user, is_active=True)

    if not course_progresses.exists():
        return Response({"is_active": False, "courses": []}, status=status.HTTP_200_OK)

    # Get all active courses the user is enrolled in
    enrolled_courses = Course.objects.filter(
        progress__student=user, progress__is_active=True
    )

    # Serialize the courses with their modules and contents
    serializer = CourseSerializer(enrolled_courses, many=True)

    # Return the serialized data along with the user's active status
    return Response(
        {"is_active": True, "courses": serializer.data}, status=status.HTTP_200_OK
    )
