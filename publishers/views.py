from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import publisher_blocked, publisher_required

from .forms import PublisherForm
from .models import Publisher
from .utils import perform_subscribe_or_unsubscribe

# Create your views here.


@login_required
def publishers(request):
    """
    Display a list of all publishers on the platform.

    Access Control:
        - User must be authenticated.

    Business Logic:
        - Retrieves all Publisher instances from the database.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :returns: Rendered template with all publishers.
    :rtype: django.http.HttpResponse
    """
    all_publishers = Publisher.objects.all()

    return render(request, "publishers.html", {"publishers": all_publishers})


@login_required
def view_publisher(request, pk):
    """
    Display the details of a single publisher.

    Retrieves the Publisher instance by primary key and renders
    the publisher detail template.

    :param request: The HTTP request object.
    :param pk: Primary key of the Publisher to view.
    :return: Rendered HttpResponse with publisher details.
    """
    publisher = get_object_or_404(Publisher, pk=pk)

    return render(
        request,
        "publishers/publisher.html",
        {
            "publisher": publisher,
            "user": request.user,
        },
    )


@login_required
@publisher_required
def edit_publisher(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Edit the details of a Publisher.

    Only accessible to users with appropriate publisher permissions
    (enforced via @publisher_required).

    Handles both GET and POST requests:
        - GET: Render form pre-filled with publisher data.
        - POST: Validate form and save changes if valid, then redirect
                to the publisher detail page.

    :param request: The HTTP request object.
    :param pk: Primary key of the Publisher to edit.
    :return: Rendered HttpResponse with edit form, or redirect after save.
    """
    publisher = get_object_or_404(Publisher, pk=pk)

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect("publishers")
    else:
        form = PublisherForm(instance=publisher)

    return render(
        request,
        "publishers/edit_publisher.html",
        {"form": form, "publisher": publisher, "user": request.user},
    )


@login_required
@publisher_blocked
def subscribe_publisher(request, pk):
    """
    Subscribe or unsubscribe the current user to/from a Publisher.

    Access Control:
        - User must be authenticated.
        - User must not be blocked (enforced by @publisher_blocked decorator).

    Business Logic:
        - Retrieves the Publisher instance by primary key.
        - Determines action from POST parameter "action":
            - "subscribe": add user to publisher M2M field
            - "unsubscribe": remove user from publisher M2M field
        - Uses perform_subscribe_or_unsubscribe utility function
        for role-based handling.
        - Redirects back to publishers list after action.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :param pk: Primary key of the publisher to subscribe/unsubscribe.
    :type pk: int
    :returns: Redirect to the publishers page.
    :rtype: django.http.HttpResponseRedirect
    :raises Http404: If the Publisher does not exist.
    """
    if request.method == "POST":

        publisher = get_object_or_404(Publisher, pk=pk)
        user = request.user
        action = request.POST.get("action")

        perform_subscribe_or_unsubscribe(publisher, user, action)

    return redirect("publishers")
