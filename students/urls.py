from django.urls import path

from lessons.students_progress import activate_student, deactivate_student
from students.dashboard_views import student_dashboard
from students.enrool_view import enroll_user
from .views import CourseListAPIView, CourseDetailAPIView, CourseEnrollAPIView

urlpatterns = [
    # API endpoint for listing all courses
    path("courses/", CourseListAPIView.as_view(), name="course_list_api"),
    # API endpoint for retrieving details of a specific course using ID instead of slug
    path("courses/<int:id>/", CourseDetailAPIView.as_view(), name="course_detail_api"),
    path("enroll/", enroll_user, name="enroll_user"),
    path("dashboard/", student_dashboard, name="student_dashboard"),
    path(
        "courses/<int:id>/enroll/",
        CourseEnrollAPIView.as_view(),
        name="course_enroll_api",
    ),
    path(
        "courses/<int:course_id>/activate-student/<int:student_id>/",
        activate_student,
        name="activate_student",
    ),
    path(
        "courses/<int:course_id>/deactivate-student/<int:student_id>/",
        deactivate_student,
        name="deactivate_student",
    ),
]
