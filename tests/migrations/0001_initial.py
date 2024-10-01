# Generated by Django 5.0.3 on 2024-09-30 20:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("lessons", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question_type",
                    models.CharField(
                        choices=[("MCQ", "Multiple Choice"), ("TEXT", "Text Answer")],
                        default="MCQ",
                        max_length=4,
                    ),
                ),
                ("text", models.TextField()),
                ("option_a", models.CharField(blank=True, max_length=255, null=True)),
                ("option_b", models.CharField(blank=True, max_length=255, null=True)),
                ("option_c", models.CharField(blank=True, max_length=255, null=True)),
                ("option_d", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "correct_answer",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "selected_option",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
                ("text_answer", models.TextField(blank=True, null=True)),
                ("is_correct", models.BooleanField(default=False)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="tests.question",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Test",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("total_marks", models.IntegerField()),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tests",
                        to="lessons.module",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="question",
            name="test",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="tests.test",
            ),
        ),
    ]
