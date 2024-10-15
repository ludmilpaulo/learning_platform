from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Module, Text, Video, Image, File, Content
from .serializers import ContentSerializer

import logging

logger = logging.getLogger(__name__)


class CreateContentView(generics.CreateAPIView):
    serializer_class = ContentSerializer  # Add the serializer_class here
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # For handling file uploads

    def perform_create(self, serializer):
        module_id = self.kwargs["module_id"]
        content_type = self.request.data.get("content_type").lower()

        # Validate module
        try:
            module = Module.objects.get(pk=module_id)
        except Module.DoesNotExist:
            raise ValidationError("Module not found.")

        # Ownership validation
        if module.course.owner != self.request.user:
            raise PermissionDenied(
                "You do not have permission to add content to this module."
            )

        # Content Type Mapping
        content_type_model_map = {
            "text": Text,
            "video": Video,
            "image": Image,
            "file": File,
        }

        if content_type not in content_type_model_map:
            raise ValidationError({"content_type": "Invalid content type."})

        # Handle content creation
        content_model = content_type_model_map[content_type]

        if content_type == "text":
            text_content = Text.objects.create(
                owner=self.request.user,
                title=self.request.data.get("title", "Text Content"),
                content=self.request.data.get("content"),
            )
            serializer.save(
                module=module,
                content_type=ContentType.objects.get_for_model(Text),
                object_id=text_content.id,
            )

        elif content_type == "video":
            video_content = Video.objects.create(
                owner=self.request.user,
                title=self.request.data.get("title", "Video Content"),
                url=self.request.data.get("url"),
            )
            serializer.save(
                module=module,
                content_type=ContentType.objects.get_for_model(Video),
                object_id=video_content.id,
            )

        elif content_type == "image":
            image_file = self.request.FILES.get("file")
            if not image_file:
                raise ValidationError("Image file is required.")
            image_content = Image.objects.create(
                owner=self.request.user,
                title=self.request.data.get("title", "Image Content"),
                file=image_file,
            )
            serializer.save(
                module=module,
                content_type=ContentType.objects.get_for_model(Image),
                object_id=image_content.id,
            )

        elif content_type == "file":
            file_upload = self.request.FILES.get("file")
            if not file_upload:
                raise ValidationError("File is required.")
            file_content = File.objects.create(
                owner=self.request.user,
                title=self.request.data.get("title", "File Content"),
                file=file_upload,
            )
            serializer.save(
                module=module,
                content_type=ContentType.objects.get_for_model(File),
                object_id=file_content.id,
            )

        logger.info(
            f"Successfully created content: {content_type} for module {module.id}"
        )
