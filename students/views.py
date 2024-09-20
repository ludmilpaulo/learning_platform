from lessons.models import Course
from lessons.serializers import CourseSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response

class CourseListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'id'  # Use 'id' instead of 'slug'
    permission_classes = [permissions.AllowAny]

class CourseEnrollAPIView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'id'  # Use 'id' instead of 'slug'

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)  # Add the authenticated user to the course's students
        return Response(status=204)
