from django.contrib import admin
from .models import (
    Subject,
    Course,
    Module,
    Content,
    Text,
    File,
    Image,
    Video,
    CourseProgress,
)


# Subject Admin
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}


# Module Inline to display within Course
class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1


# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "owner", "created"]
    list_filter = ["created", "subject"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]


# Content Inline to display within Module
class ContentInline(admin.StackedInline):
    model = Content
    extra = 1


# Module Admin
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "order"]
    list_filter = ["course"]
    search_fields = ["title"]
    inlines = [ContentInline]


# Text, Image, Video, File Admins
@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created"]
    search_fields = ["title", "content"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created"]
    search_fields = ["title"]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created"]
    search_fields = ["title", "url"]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created"]
    search_fields = ["title", "file"]


# Content Admin
@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["module", "content_type", "object_id", "order"]
    list_filter = ["module", "content_type"]
    search_fields = ["module__title"]


# CourseProgress Admin
@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "course"]
    search_fields = ["student__username", "course__title"]
    list_filter = ["course"]
    filter_horizontal = ["completed_modules", "completed_contents"]
