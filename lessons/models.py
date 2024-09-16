from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.loader import render_to_string
from .fields import OrderField

# Existing models (Subject, Course, Module, Content, etc.) stay the same

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        User, related_name="courses_created", on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject, related_name="courses", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="courses/%Y/%m/%d", blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name="courses_joined", blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=["course"])

    def __str__(self):
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ["order"]


class Content(models.Model):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    order = OrderField(blank=True, for_fields=["module"])

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    owner = models.ForeignKey(
        User, related_name="%(class)s_related", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title




class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    file = models.FileField(upload_to="images")


class Video(ItemBase):
    url = models.URLField()


#################################################################################
# Progress Tracking

class CourseProgress(models.Model):
    student = models.ForeignKey(User, related_name="progress", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="progress", on_delete=models.CASCADE)
    completed_modules = models.ManyToManyField(Module, related_name="completed_by_students", blank=True)
    completed_contents = models.ManyToManyField(Content, related_name="completed_by_students", blank=True)
    last_accessed_module = models.ForeignKey(Module, null=True, blank=True, related_name="last_accessed_by", on_delete=models.SET_NULL)

    def get_progress_percentage(self):
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 0
        completed_modules_count = self.completed_modules.count()
        return (completed_modules_count / total_modules) * 100

    def get_content_progress_percentage(self, module):
        total_contents = module.contents.count()
        if total_contents == 0:
            return 0
        completed_content_count = self.completed_contents.filter(module=module).count()
        return (completed_content_count / total_contents) * 100

    def __str__(self):
        return f"{self.student.username}'s progress in {self.course.title}"
