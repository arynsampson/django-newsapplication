from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse


def journalist_required(view_func):
    """
    Decorator to restrict access to Journalist users only.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != "Journalist":
            return redirect(reverse("home"))
        return view_func(request, *args, **kwargs)

    return wrapper


def journalist_editor_required(view_func):
    """
    Decorator to restrict access to Journalist and Editor users only.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role not in ["Journalist", "Editor"]:
            return redirect(reverse("home"))
        return view_func(request, *args, **kwargs)

    return wrapper


def reader_required(view_func):
    """
    Decorator to restrict access to Reader users only.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != "Reader":
            return redirect(reverse("home"))
        return view_func(request, *args, **kwargs)

    return wrapper


def publisher_blocked(view_func):
    """
    Decorator to restrict Publishers from accessing.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "Publisher":
            return redirect(reverse("home"))
        return view_func(request, *args, **kwargs)

    return wrapper


def publisher_required(view_func):
    """
    Decorator to restrict accesss to Publishers only.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != "Publisher":
            return redirect(reverse("home"))
        return view_func(request, *args, **kwargs)

    return wrapper
