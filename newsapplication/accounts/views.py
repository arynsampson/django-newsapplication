from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from articles.models import Article
from core.decorators import reader_required
from publishers.models import Publisher

from .forms import RegisterForm
from .utils import assign_user_role_and_permissions

# Get the active user model
User = get_user_model()
# Create your views here.


def register(request: HttpRequest) -> HttpResponse:
    """
    Handle user registration and optional publisher account creation.

    Redirects authenticated users to the home page. On POST, validates the
    registration form, creates a User instance, optionally
    creates a Publisher
    account if the role is 'Publisher', logs in the new user, and redirects
    to the home page. On GET, displays the empty registration form.

    Notes:
        - The 'role' field in POST determines whether a Publisher account
          should be created.
        - Uses Django's login() to authenticate the user immediately after
          registration.

    :param request: The HTTP request object containing GET or POST data
    :type request: HttpRequest
    :return: HttpResponse object, either a redirect to home or rendered
        template
    :rtype: HttpResponse

    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form: RegisterForm = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if request.POST.get("role") == "Publisher":
                Publisher.objects.create(
                    name=form.cleaned_data["username"], owner=user
                )
            assign_user_role_and_permissions(user)
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


def login_user(request: HttpRequest) -> HttpResponse:
    """
    Handle user login and session management.

    Redirects authenticated users to home. On POST, validates
    the authentication
    form, logs in the user, sets the session expiry to 1 hour,
    and redirects to
    home. On GET, displays the empty login form.

    Notes:
        - Uses Django's AuthenticationForm for validation.
        - Sets session expiry with request.session.set_expiry(3600).

    :param request: The HTTP request object containing GET or POST data
    :type request: HttpRequest
    :return: HttpResponse object, either a redirect to home or
        rendered template
    :rtype: HttpResponse

    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form: AuthenticationForm = AuthenticationForm(
            request, data=request.POST
        )
        if form.is_valid():
            user: User = form.get_user()
            request.session.set_expiry(3600)
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(
        request,
        "auth/login.html",
        {"form": form, "user": request.user.is_authenticated},
    )


@login_required
def logout_user(request: HttpRequest) -> HttpResponse:
    """
    Log out the currently authenticated user.

    Uses Django's logout() to clear the session and redirect to
    the login page.

    :param request: The HTTP request object
    :type request: HttpRequest
    :return: HttpResponse object redirecting to the login page
    :rtype: HttpResponse
    """
    logout(request)
    return redirect("login")


# USER PROFILE
@login_required
def user_profile(request, pk):
    """
    Display a public user profile page.

    This view retrieves a user by primary key and renders their profile.

    Access Control:
        - User must be authenticated.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: Primary key of the user whose profile is being viewed.
    :type pk: int
    :returns: Rendered profile template with user context.
    :rtype: django.http.HttpResponse
    :raises Http404: If no user exists with the given primary key.
    """
    user = get_object_or_404(User, pk=pk)
    
    if user != request.user:
        return redirect("home")
    
    return render(request, "user/profile.html", {"user": user})


# JOURNALISTS
@login_required
def journalists(request):
    """
    Display a list of all users with the Journalist role.

    Access Control:
        - User must be authenticated.

    Business Logic:
        - Filters users by role="Journalist".

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :returns: Rendered template containing all journalists.
    :rtype: django.http.HttpResponse
    """
    all_journalists = User.objects.filter(role="Journalist")

    return render(
        request, "journalists.html", {"journalists": all_journalists}
    )


@login_required
@reader_required
def subscribe_jounalist(request, pk):
    """
    Subscribe or unsubscribe a Reader to/from a Journalist.

    This view allows a Reader to:
        - Subscribe to a journalist
        - Unsubscribe from a journalist

    Access Control:
        - User must be authenticated.
        - Only users with role="Reader" can access and subscribe/unsubscribe.

    Business Rules:
        - Action is determined by POST parameter "action".
        - Valid actions: "subscribe", "unsubscribe".
        - After processing, user is redirected to journalist list.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: Primary key of the journalist.
    :type pk: int
    :returns: Redirect response to journalists page.
    :rtype: django.http.HttpResponseRedirect
    :raises Http404: If the journalist does not exist.
    """
    # The journalist being subscribed to/unsubscribed from
    journalist = get_object_or_404(User, pk=pk)
    reader = request.user

    if request.method == "POST" and reader.role == "Reader":
        action = request.POST.get("action")

        try:
            if action == "subscribe":
                reader.subscribed_journalists.add(journalist)

            elif action == "unsubscribe":
                reader.subscribed_journalists.remove(journalist)
        except Exception as e:
            return HttpResponse(f"Error occured: {e}")

    return redirect("journalists")


@login_required
def journalist_profile(request, pk):
    journalist = get_object_or_404(User, pk=pk)
    journalist_articles = Article.objects.filter(author=journalist)

    return render(
        request,
        "journalist_profile.html",
        {
            "journalist": journalist,
            "articles": journalist_articles,
            "user": request.user,
        },
    )
