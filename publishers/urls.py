from django.urls import path

from . import views

urlpatterns = [
    path("publishers/", views.publishers, name="publishers"),
    path("publisher/<int:pk>/", views.view_publisher, name="view_publisher"),
    path(
        "publisher/<int:pk>/edit/", views.edit_publisher, name="edit_publisher"
    ),
    path(
        "publishers/<int:pk>/subscribe",
        views.subscribe_publisher,
        name="subscribe_publisher",
    ),
]
