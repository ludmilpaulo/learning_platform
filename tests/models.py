from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from lessons.models import Module  # Import the Module model


class Test(models.Model):
    """Model representing a test for a specific module."""

    module = models.ForeignKey(Module, related_name="tests", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_marks = models.IntegerField()

    def __str__(self):
        return f"Test: {self.name} for {self.module.title}"

    def is_active(self):
        """Check if the test is currently active."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class Question(models.Model):
    """Model representing a question in the test."""

    QUESTION_TYPE_CHOICES = [
        ("MCQ", "Multiple Choice"),
        ("TEXT", "Text Answer"),
    ]

    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    question_type = models.CharField(
        max_length=4, choices=QUESTION_TYPE_CHOICES, default="MCQ"
    )
    text = models.TextField()
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(
        max_length=1, blank=True, null=True
    )  # A, B, C, or D for MCQ

    def __str__(self):
        return f"{self.text} (Test: {self.test.name})"


class Answer(models.Model):
    """Model to store student answers for the questions."""

    student = models.ForeignKey(User, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    selected_option = models.CharField(
        max_length=1, blank=True, null=True
    )  # A, B, C, D for MCQ
    text_answer = models.TextField(blank=True, null=True)  # For text-based answers
    is_correct = models.BooleanField(default=False)  # For MCQ answers

    def save(self, *args, **kwargs):
        """Automatically evaluate if the answer is correct for MCQ questions."""
        if self.question.question_type == "MCQ":
            self.is_correct = self.selected_option == self.question.correct_answer
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer by {self.student.username} for {self.question.text}"
