from django.urls import path

from lessons.tutor_content import ContentCreateView, CreateFileView, CreateImageView, CreateTextView, CreateVideoView, get_content_types
from lessons.tutor_views import ContentDetailView, ContentListView, ModuleDetailView, ModuleListCreateView
from .views import (
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
    
    path('text/', CreateTextView.as_view(), name='create-text'),
    
    # Video Content URL
    path('video/', CreateVideoView.as_view(), name='create-video'),
    
    # Image Content URL
    path('image/', CreateImageView.as_view(), name='create-image'),
    
    # File Content URL
    path('file/', CreateFileView.as_view(), name='create-file'),

    # Content CRUD
    path('modules/<int:module_id>/contents/', ContentCreateView.as_view(), name='content-create'),
    path('modules_view/<int:module_id>/contents/', ContentListView.as_view(), name='content-create'),
    path('contents/<int:pk>/', ContentDetailView.as_view(), name='content-detail'),
    path('courses/', CreateCourseView.as_view(), name='course-create'),
    path('courses/user/', UserCoursesView.as_view(), name='user_courses'),  # Adjust this path if needed
    path('progress/', CourseProgressListCreateView.as_view(), name='progress_list_create'),
    path('progress/<int:pk>/', CourseProgressDetailView.as_view(), name='progress_detail'),
    path('progress/<int:pk>/content/<int:content_id>/complete/', MarkContentCompleteView.as_view(), name='mark_content_complete'),
]
