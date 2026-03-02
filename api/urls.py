from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/articles/", views.articles, name="api_articles"),
    path("api/article/<int:pk>/", views.article, name="api_article"),
    path(
        "api/article/create/", views.article_create, name="api_create_article"
    ),
    path(
        "api/article/<int:pk>/delete/",
        views.article_delete,
        name="api_delete_article",
    ),
    path(
        "api/articles/subscribed/",
        views.subscriber_articles,
        name="api-subscriber_articles",
    ),
    path(
        "api/article/<int:pk>/update/",
        views.article_update,
        name="api-article_update",
    ),
]
