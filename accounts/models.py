from django.db import models
from django.contrib.auth.models import User

from lessons.models import Course, Subject


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    id_number_or_passport = models.CharField(max_length=30, blank=True)
    gender = models.CharField(
        max_length=10, choices=[("male", "Male"), ("female", "Female")], blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        abstract = True


class TutorProfile(BaseProfile):
    qualifications = models.TextField(blank=True)  # Tutor's qualifications
    experience_years = models.IntegerField(
        null=True, blank=True
    )  # Years of experience as a tutor
    subjects = models.ManyToManyField(
        Subject, blank=True
    )  # Subjects the tutor can teach
    enrolled_courses = models.ManyToManyField(Course, blank=True)
    hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )  # Tutor's hourly rate
    is_active = models.BooleanField(
        default=True
    )  # Whether the tutor is actively teaching

    def __str__(self):
        return f"Tutor Profile: {self.name} {self.surname}"


class StudentProfile(BaseProfile):
    enrolled_courses = models.ManyToManyField(
        Course, blank=True
    )  # Courses the student is enrolled in
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Student Profile: {self.name} {self.surname}"
