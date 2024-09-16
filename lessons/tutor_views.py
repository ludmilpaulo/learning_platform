from rest_framework import generics
from .models import Module, Content, Course, Text, File, Image, Video
from .serializers import ModuleSerializer, ContentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class ModuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensure the user only accesses modules for courses they own.
        """
        course_id = self.kwargs['course_id']
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found.")

        # Check if the course belongs to the logged-in user
        if course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to access this course.")

        # Return the modules related to the course
        return Module.objects.filter(course=course)

    def perform_create(self, serializer):
        """
        Override perform_create to ensure the course is linked to the new module.
        """
        course_id = self.kwargs['course_id']
        course = Course.objects.get(pk=course_id)

        # Ensure the course belongs to the logged-in user
        if course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to add modules to this course.")

        # Save the new module with the linked course
        serializer.save(course=course)

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Module.objects.all()

from rest_framework import generics
from .models import Content, Module, Text, Image, Video, File
from .serializers import ContentSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError

class ContentCreateView(generics.CreateAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        module_id = self.kwargs['module_id']
        module = Module.objects.get(pk=module_id)

        # Check that the module belongs to the logged-in user's course
        if module.course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to add content to this module.")

        # Get content_type (e.g., Text, Image, Video) from the request data
        content_type_name = self.request.data.get('content_type')
        content_model = ContentType.objects.get(model=content_type_name.lower())

        # Validate the object ID (e.g., ID of the specific Text, Image, etc.)
        object_id = self.request.data.get('object_id')
        if not object_id:
            raise ValidationError("object_id is required.")

        serializer.save(module=module, content_type=content_model, object_id=object_id)

import logging

logger = logging.getLogger(__name__)

class ContentListView(generics.ListAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module_id = self.kwargs['module_id']
        module = Module.objects.get(pk=module_id)

        if module.course.owner != self.request.user:
            raise PermissionDenied("You do not have permission to view contents for this module.")
        
        return Content.objects.filter(module=module)



class ContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Content.objects.all()
