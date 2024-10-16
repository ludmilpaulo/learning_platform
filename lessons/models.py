from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField

# Core models for subjects, courses, modules, and content.


class Subject(models.Model):
    """Model representing a subject or category of courses."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(models.Model):
    """Model representing a course, which contains multiple modules."""

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

    def get_students_progress(self):
        """
        Get progress of all students enrolled in the course.
        """
        progress_list = []
        for student in self.students.all():
            progress = CourseProgress.objects.filter(
                student=student, course=self
            ).first()
            if progress:
                student_progress = {
                    "student_id": student.id,
                    "student": student.username,
                    "progress_percentage": progress.get_progress_percentage(),
                    "completed_modules": progress.completed_modules.count(),
                    "total_modules": self.modules.count(),
                    "completed_contents": progress.completed_contents.count(),
                    "total_contents": sum(
                        module.contents.count() for module in self.modules.all()
                    ),
                }
            else:
                student_progress = {
                    "student_id": student.id,
                    "student": student.username,
                    "progress_percentage": 0,
                    "completed_modules": 0,
                    "total_modules": self.modules.count(),
                    "completed_contents": 0,
                    "total_contents": sum(
                        module.contents.count() for module in self.modules.all()
                    ),
                }

            progress_list.append(student_progress)

        return progress_list


class Module(models.Model):
    """Model representing a module in a course, which can contain multiple contents."""

    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=["course"])

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"


class Content(models.Model):
    """Generic content model for different types of course contents (text, video, image, file)."""

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
    """Abstract model for different types of content items like text, video, image, and file."""

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


# Concrete content types inheriting from ItemBase.
class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    file = models.FileField(upload_to="images")


class Video(ItemBase):
    url = models.URLField()


class Live(ItemBase):
    url = models.URLField()


#################################################################################
class CourseProgress(models.Model):
    student = models.ForeignKey(User, related_name="progress", on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, related_name="progress", on_delete=models.CASCADE
    )
    completed_modules = models.ManyToManyField(
        Module, related_name="completed_by_students", blank=True
    )
    completed_contents = models.ManyToManyField(
        Content, related_name="completed_by_students", blank=True
    )
    last_accessed_module = models.ForeignKey(
        Module,
        null=True,
        blank=True,
        related_name="last_accessed_by",
        on_delete=models.SET_NULL,
    )
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        auto_now_add=True
    )  # Automatically set when the progress is created
    date_completed = models.DateTimeField(
        null=True, blank=True
    )  # Set when the course is completed

    # Your existing methods...

    def get_progress_percentage(self):
        """Calculate overall progress as a percentage based on completed modules."""
        total_modules = self.course.modules.count()
        if total_modules == 0:
            return 0
        completed_modules_count = self.completed_modules.count()
        return (completed_modules_count / total_modules) * 100

    def get_content_progress_percentage(self, module):
        """Calculate progress within a specific module based on completed content."""
        total_contents = module.contents.count()
        if total_contents == 0:
            return 0
        completed_content_count = self.completed_contents.filter(module=module).count()
        return (completed_content_count / total_contents) * 100

    def __str__(self):
        return f"{self.student.username}'s progress in {self.course.title}"
