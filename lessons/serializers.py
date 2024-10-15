from rest_framework import serializers
from .models import CourseProgress, Course, Module, Content, Text, File, Image, Video


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "subject", "overview", "image", "created"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "title", "description", "order"]
        read_only_fields = ["course"]


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ["id", "title", "content", "created", "updated"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "title", "file", "created", "updated"]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "title", "url", "created", "updated"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "title", "file", "created", "updated"]


class ContentSerializer(serializers.ModelSerializer):
    # Add dynamic fields for the content types
    content_data = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = [
            "id",
            "module",
            "content_type",
            "object_id",
            "content_data",
        ]  # Add 'content_data' field

    def get_content_data(self, obj):
        # Check the type of content and return the appropriate data
        content_type = obj.content_type.model

        if content_type == "text":
            return TextSerializer(obj.item).data
        elif content_type == "image":
            return ImageSerializer(obj.item).data
        elif content_type == "video":
            return VideoSerializer(obj.item).data
        elif content_type == "file":
            return FileSerializer(obj.item).data
        else:
            return None  # Handle cases where the content type is not recognized


class CourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    completed_modules = ModuleSerializer(many=True, read_only=True)
    completed_contents = ContentSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CourseProgress
        fields = [
            "id",
            "course",
            "completed_modules",
            "completed_contents",
            "last_accessed_module",
            "progress_percentage",
        ]

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
