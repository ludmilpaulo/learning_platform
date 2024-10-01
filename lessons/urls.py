from django.urls import path

from lessons.content import CreateContentView
from lessons.students_progress import get_students_progress
from lessons.tutor_content import create_content
from lessons.tutor_module import add_module_to_course
from lessons.tutor_module_contents import get_module_contents
from lessons.tutor_views import ContentDetailView, ContentListView, ModuleDetailView, ModuleListCreateView, get_content_types
from .views import (
    CourseDetailView,
    CourseProgressListCreateView,
    CourseProgressDetailView,
    CreateCourseView,
    MarkContentCompleteView,
    UserCoursesView,
)

urlpatterns = [
    path('courses/<int:course_id>/modules/', ModuleListCreateView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('get-content-types/', get_content_types, name='get-content-types'),
    path('courses/<int:course_id>/students-progress/', get_students_progress, name='students-progress'),

    # Content CRUD
    path('modules/<int:module_id>/contents/', create_content, name='content-create'),
    path('modules/<int:module_id>/get_contents/', get_module_contents, name='module-contents'),
    path('modules_view/<int:module_id>/contents/', ContentListView.as_view(), name='content-create'),
    path('courses/<int:course_id>/modules/', add_module_to_course, name='add_module_to_course'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),  # Added this route
    path('contents/<int:pk>/', ContentDetailView.as_view(), name='content-detail'),
    path('courses/', CreateCourseView.as_view(), name='course-create'),
    path('courses/user/', UserCoursesView.as_view(), name='user_courses'),  # Adjust this path if needed
    path('progress/', CourseProgressListCreateView.as_view(), name='progress_list_create'),
    path('progress/<int:pk>/', CourseProgressDetailView.as_view(), name='progress_detail'),
    path('progress/<int:pk>/content/<int:content_id>/complete/', MarkContentCompleteView.as_view(), name='mark_content_complete'),
]
