from rest_framework import serializers
from .models import CourseProgress, Course, Module, Content

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'subject', 'overview', 'image', 'created']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order']
        read_only_fields = ['course'] 

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'module', 'content_type', 'object_id']
        
    
class CourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    completed_modules = ModuleSerializer(many=True, read_only=True)
    completed_contents = ContentSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CourseProgress
        fields = ['id', 'course', 'completed_modules', 'completed_contents', 'last_accessed_module', 'progress_percentage']

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()


from rest_framework import serializers
from .models import Content, Text, File, Image, Video

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'module', 'content_type', 'object_id', 'item']

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ['id', 'title', 'content']

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'title', 'file']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'title', 'file']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'url']
