from django.urls import path
from . import views

urlpatterns = [
    path("modules/<int:module_id>/create_test/", views.create_test, name="create_test"),
    path(
        "tests/<int:test_id>/submit_answers/",
        views.submit_test_answers,
        name="submit_test_answers",
    ),
    path(
        "tests/<int:test_id>/results/",
        views.view_test_results,
        name="view_test_results",
    ),
]
