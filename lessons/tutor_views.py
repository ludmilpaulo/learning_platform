from rest_framework import generics
from .models import Module, Content, Course, Text, File, Image, Video
from .serializers import ModuleSerializer, ContentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view


class ModuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found.")

        # Ensure the course belongs to the logged-in user
        if course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this course.")

        return Module.objects.filter(course=course)

    def perform_create(self, serializer):
        course_id = self.kwargs["course_id"]
        course = Course.objects.get(pk=course_id)

        if course.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add modules to this course."
            )

        serializer.save(course=course)


# New class to handle retrieve, update (edit), and delete for individual modules
class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restrict access to modules belonging to the course owned by the user.
        """
        course_id = self.kwargs["course_id"]
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found.")

        if course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this course.")

        return Module.objects.filter(course=course)

    def update(self, request, *args, **kwargs):
        """
        Handle updating a module if the user owns the course.
        """
        try:
            module = self.get_object()
            if module.course.owner != request.user:
                raise PermissionDenied("You don't have permission to edit this module.")

            return super().update(request, *args, **kwargs)

        except Module.DoesNotExist:
            return Response(
                {"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        """
        Handle deleting a module if the user owns the course.
        """
        try:
            module = self.get_object()
            if module.course.owner != request.user:
                raise PermissionDenied(
                    "You don't have permission to delete this module."
                )

            return super().destroy(request, *args, **kwargs)

        except Module.DoesNotExist:
            return Response(
                {"error": "Module not found"}, status=status.HTTP_404_NOT_FOUND
            )


from rest_framework import generics
from .models import Content, Module, Text, Image, Video, File
from .serializers import ContentSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError


class ContentCreateView(generics.CreateAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        module_id = self.kwargs["module_id"]
        module = Module.objects.get(pk=module_id)

        # Check that the module belongs to the logged-in user's course
        if module.course.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add content to this module."
            )

        # Get content_type (e.g., Text, Image, Video) from the request data
        content_type_name = self.request.data.get("content_type")
        content_model = ContentType.objects.get(model=content_type_name.lower())

        # Validate the object ID (e.g., ID of the specific Text, Image, etc.)
        object_id = self.request.data.get("object_id")
        if not object_id:
            raise ValidationError("object_id is required.")

        serializer.save(module=module, content_type=content_model, object_id=object_id)


import logging

logger = logging.getLogger(__name__)


class ContentListView(generics.ListAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module_id = self.kwargs["module_id"]
        module = Module.objects.get(pk=module_id)
        user = self.request.user

        # Check if the user is the course owner or a student in the course
        if (
            module.course.owner != user
            and not module.course.students.filter(id=user.id).exists()
        ):
            raise PermissionDenied(
                "You do not have permission to view contents for this module."
            )

        return Content.objects.filter(module=module)


class ContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Content.objects.all()


from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_content_types(request):
    """API to get content type mappings dynamically."""
    try:
        content_types = {
            "text": ContentType.objects.get(model="text").id,
            "image": ContentType.objects.get(model="image").id,
            "video": ContentType.objects.get(model="video").id,
            "file": ContentType.objects.get(model="file").id,
        }
        return Response(content_types, status=status.HTTP_200_OK)
    except ContentType.DoesNotExist:
        return Response(
            {"error": "Failed to retrieve content types."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
