from rest_framework import serializers
from lessons.models import Text, File, Image, Video, Course, Module


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ["title", "content"]  # Include fields that you want to serialize


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["title", "file"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["title", "file"]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["title", "url"]


class ModuleSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ["title", "description", "order", "contents"]

    def get_contents(self, obj):
        # Serialize the contents based on their type
        contents = []
        for content in obj.contents.all():
            if isinstance(content.item, Text):
                contents.append(TextSerializer(content.item).data)
            elif isinstance(content.item, File):
                contents.append(FileSerializer(content.item).data)
            elif isinstance(content.item, Image):
                contents.append(ImageSerializer(content.item).data)
            elif isinstance(content.item, Video):
                contents.append(VideoSerializer(content.item).data)
        return contents


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True)  # Include related modules

    class Meta:
        model = Course
        fields = ["title", "overview", "progress", "modules"]
