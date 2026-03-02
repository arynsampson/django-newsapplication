from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("user/<int:pk>/", views.user_profile, name="user_profile"),
    path(
        "journalist/<int:pk>/",
        views.journalist_profile,
        name="journalist_profile",
    ),
    path("journalists/", views.journalists, name="journalists"),
    path(
        "journalist/<int:pk>/subscribe/",
        views.subscribe_jounalist,
        name="subscribe_jounalist",
    ),
]
