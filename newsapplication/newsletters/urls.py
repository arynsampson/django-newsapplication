from django.urls import path

from . import views

urlpatterns = [
    path("newsletters/", views.newsletters, name="newsletters"),
    path(
        "newsletter/<int:pk>/", views.view_newsletter, name="view_newsletter"
    ),
    path(
        "newsletter/<int:pk>/edit",
        views.edit_newsletter,
        name="edit_newsletter",
    ),
    path(
        "newsletters/create", views.create_newsletter, name="create_newsletter"
    ),
    path(
        "newsletter/<int:pk>/delete",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    path(
        "newsletter/<int:npk>/article/<int:apk>/add",
        views.add_article,
        name="add_article",
    ),
    path(
        "newsletter/<int:npk>/article/<int:apk>/remove",
        views.remove_article,
        name="remove_article",
    ),
]
