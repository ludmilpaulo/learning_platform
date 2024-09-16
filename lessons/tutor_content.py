from rest_framework import generics
from .models import Content, Module, Text, Image, Video, File
from .serializers import ContentSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
def get_content_types(request):
    # Get the content types for your specific models
    content_types = {
        'text': ContentType.objects.get(model='text').pk,
        'image': ContentType.objects.get(model='image').pk,
        'video': ContentType.objects.get(model='video').pk,
        'file': ContentType.objects.get(model='file').pk,
    }
    return Response(content_types)



import logging

logger = logging.getLogger(__name__)
class ContentCreateView(generics.CreateAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Handles file uploads

    def perform_create(self, serializer):
        # Log the incoming data and files
        logger.info(f"Request data: {self.request.data}")
        logger.info(f"Request files: {self.request.FILES}")

        # Get the module
        module_id = self.kwargs['module_id']
        try:
            module = Module.objects.get(pk=module_id)
        except Module.DoesNotExist:
            logger.error(f"Module {module_id} not found.")
            raise PermissionDenied("Module not found.")

        # Check ownership
        if module.course.owner != self.request.user:
            logger.error(f"User {self.request.user} does not have permission to add content to module {module_id}.")
            raise PermissionDenied("You do not have permission to add content to this module.")

        # Get the content type
        content_type_name = self.request.data.get('content_type')
        try:
            content_type = ContentType.objects.get(model=content_type_name.lower())
        except ContentType.DoesNotExist:
            logger.error(f"Invalid content type: {content_type_name}")
            raise ValidationError({"content_type": "Invalid content type."})

        # Process content based on type
        if content_type_name == 'text':
            content = self.request.data.get('content')
            if not content:
                logger.error("Text content is missing.")
                raise ValidationError("Text content is required.")
            logger.info("Creating text content.")
            text_content = Text.objects.create(
                owner=self.request.user,
                title=self.request.data.get('title', 'Text Content'),
                content=content
            )
            serializer.save(module=module, content_type=content_type, object_id=text_content.id)

        elif content_type_name == 'video':
            url = self.request.data.get('url')
            if not url:
                logger.error("Video URL is missing.")
                raise ValidationError("Video URL is required.")
            logger.info("Creating video content.")
            video_content = Video.objects.create(
                owner=self.request.user,
                title=self.request.data.get('title', 'Video Content'),
                url=url
            )
            serializer.save(module=module, content_type=content_type, object_id=video_content.id)

        elif content_type_name == 'image':
            if 'file' not in self.request.FILES:
                logger.error("Image file is missing.")
                raise ValidationError("Image file is required.")
            logger.info("Creating image content.")
            image_content = Image.objects.create(
                owner=self.request.user,
                title=self.request.data.get('title', 'Image Content'),
                file=self.request.FILES['file']
            )
            serializer.save(module=module, content_type=content_type, object_id=image_content.id)

        elif content_type_name == 'file':
            if 'file' not in self.request.FILES:
                logger.error("File is missing.")
                raise ValidationError("File is required.")
            logger.info("Creating file content.")
            file_content = File.objects.create(
                owner=self.request.user,
                title=self.request.data.get('title', 'File Content'),
                file=self.request.FILES['file']
            )
            serializer.save(module=module, content_type=content_type, object_id=file_content.id)

        logger.info("Content creation successful.")


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Text, Image, Video, File
from .serializers import TextSerializer, ImageSerializer, VideoSerializer, FileSerializer

# Text Content Creation View
class CreateTextView(generics.CreateAPIView):
    serializer_class = TextSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Video Content Creation View
class CreateVideoView(generics.CreateAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# Image Content Creation View
class CreateImageView(generics.CreateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For handling file uploads

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# File Content Creation View
class CreateFileView(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For handling file uploads

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
