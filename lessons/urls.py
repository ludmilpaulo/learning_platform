from django.urls import path

from lessons.content import CreateContentView
from lessons.courseProgress import mark_module_complete
from lessons.students_progress import (
    activate_student,
    deactivate_student,
    get_students_progress,
)
from lessons.tutor_content import create_content
from lessons.tutor_module import add_module_to_course
from lessons.tutor_module_contents import get_module_contents
from lessons.tutor_views import (
    ContentDetailView,
    ContentListView,
    ModuleDetailView,
    ModuleListCreateView,
    get_content_types,
)
from students.module_content import mark_content_complete
from .views import (
    CourseDetailView,
    CourseProgressListCreateView,
    CourseProgressDetailView,
    CreateCourseView,
    MarkContentCompleteView,
    RemoveStudentFromCourseView,
    UserCoursesView,
)

urlpatterns = [
    path(
        "courses/<int:course_id>/modules/",
        ModuleListCreateView.as_view(),
        name="module-list-create",
    ),
    path("modules/<int:pk>/", ModuleDetailView.as_view(), name="module-detail"),
    path(
        "courses/<int:course_id>/modules/<int:pk>/",
        ModuleDetailView.as_view(),
        name="module-detail",
    ),
    path("get-content-types/", get_content_types, name="get-content-types"),
    path(
        "courses/<int:course_id>/students-progress/",
        get_students_progress,
        name="students-progress",
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
    # Content CRUD
    path("modules/<int:module_id>/contents/", create_content, name="content-create"),
    path(
        "modules/<int:module_id>/get_contents/",
        get_module_contents,
        name="module-contents",
    ),
    path(
        "modules_view/<int:module_id>/contents/",
        ContentListView.as_view(),
        name="content-create",
    ),
    path(
        "courses/<int:course_id>/modules/",
        add_module_to_course,
        name="add_module_to_course",
    ),
    path(
        "courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"
    ),  # Added this route
    path("contents/<int:pk>/", ContentDetailView.as_view(), name="content-detail"),
    path("courses/", CreateCourseView.as_view(), name="course-create"),
    path(
        "courses/user/", UserCoursesView.as_view(), name="user_courses"
    ),  # Adjust this path if needed
    path(
        "progress/", CourseProgressListCreateView.as_view(), name="progress_list_create"
    ),
    path(
        "progress/<int:pk>/", CourseProgressDetailView.as_view(), name="progress_detail"
    ),
    path(
        "progress/<int:pk>/content/<int:content_id>/complete/",
        MarkContentCompleteView.as_view(),
        name="mark_content_complete",
    ),
    path('courses/<int:course_id>/content/<int:content_id>/complete/', mark_content_complete, name='mark_content_complete'),
  #  path('courses/<int:course_id>/module/<int:module_id>/complete/', mark_module_complete, name='mark_module_complete'),
    path('courses/<int:course_id>/remove-student/<int:student_id>/', RemoveStudentFromCourseView.as_view(), name='remove-student'),
    path("mark_module_complete/<int:course_id>/<int:module_id>/", mark_module_complete, name="mark_module_complete"),

]
