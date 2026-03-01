from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from MySQLdb import DatabaseError

from articles.models import Article
from core.decorators import journalist_editor_required

from .forms import NewsletterForm
from .models import Newsletter


# Create your views here.
@login_required
def newsletters(request):
    """
    Display a list of all newsletters.

    Access Control:
        - User must be authenticated.

    Retrieves all Newsletter instances from the database and renders
    them in the newsletters template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :returns: Rendered template with all newsletters.
    :rtype: HttpResponse
    """
    all_newsletters = Newsletter.objects.all()
    return render(
        request, "newsletters.html", {"newsletters": all_newsletters}
    )


@login_required
@journalist_editor_required
def create_newsletter(request):
    """
    Create a new newsletter.

    Access Control:
        - User must be authenticated.
        - User must be a Journalist or Editor (enforced by decorator).

    Handles POST requests for form submission and GET requests to display
    an empty form. Sets the current user as the author on save.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :returns: Rendered form template on GET or redirect
    after successful creation.
    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                newsletter = form.save(commit=False)
                newsletter.author = request.user
                newsletter.save()
                return redirect("newsletters")
            except DatabaseError as e:
                return HttpResponse(f"Error occured: {e}")
    else:
        form = NewsletterForm()

    return render(
        request,
        "newsletters/create_newsletter.html",
        {
            "form": form,
        },
    )


@login_required
def view_newsletter(request, pk):
    """
    View a single newsletter and its associated articles.

    Access Control:
        - User must be authenticated.

    Also provides a list of articles not yet added to the newsletter.

    :param request: The HTTP request object.
    :param pk: Primary key of the newsletter to view.
    :type request: HttpRequest
    :type pk: int
    :returns: Rendered newsletter detail template.
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    available_articles = Article.objects.exclude(
        pk__in=newsletter.articles.values_list("pk", flat=True)
    )

    return render(
        request,
        "newsletters/newsletter.html",
        {
            "newsletter": newsletter,
            "available_articles": available_articles,
            "user": request.user,
        },
    )


@login_required
@journalist_editor_required
def edit_newsletter(request, pk):
    """
    Edit an existing newsletter.

    Access Control:
        - User must be authenticated.
        - User must be a Journalist or Editor.

    Handles POST requests to update the newsletter and GET requests
    to display the form pre-filled with existing data.

    :param request: The HTTP request object.
    :param pk: Primary key of the newsletter to edit.
    :type request: HttpRequest
    :type pk: int
    :returns: Rendered edit form template on GET or redirect to
    view on POST.
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()

            return redirect("view_newsletter", pk=newsletter.pk)
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "newsletters/edit_newsletter.html",
        {"form": form, "newsletter": newsletter, "user": request.user},
    )


@login_required
@journalist_editor_required
def add_article(request, npk, apk):
    """
    Add an article to a newsletter.

    Access Control:
        - User must be authenticated.
        - User must be a Journalist or Editor.

    :param request: The HTTP request object.
    :param npk: Primary key of the newsletter.
    :param apk: Primary key of the article to add.
    :type request: HttpRequest
    :type npk: int
    :type apk: int
    :returns: Redirect to the newsletter detail page.
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=npk)
    article = get_object_or_404(Article, pk=apk)

    newsletter.articles.add(article)

    return redirect("view_newsletter", pk=npk)


@login_required
@journalist_editor_required
def remove_article(request, npk, apk):
    """
    Remove an article from a newsletter.

    Access Control:
        - User must be authenticated.
        - User must be a Journalist or Editor.

    :param request: The HTTP request object.
    :param npk: Primary key of the newsletter.
    :param apk: Primary key of the article to remove.
    :type request: HttpRequest
    :type npk: int
    :type apk: int
    :returns: Redirect to the newsletter detail page.
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=npk)
    article = get_object_or_404(Article, pk=apk)

    newsletter.articles.remove(article)

    return redirect("view_newsletter", pk=npk)


@login_required
@journalist_editor_required
def delete_newsletter(request, pk):
    """
    Delete a newsletter.

    Access Control:
        - User must be authenticated.
        - User must be a Journalist or Editor.

    :param request: The HTTP request object.
    :param pk: Primary key of the newsletter to delete.
    :type request: HttpRequest
    :type pk: int
    :returns: Redirect to the newsletters list page.
    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    newsletter.delete()
    return redirect("newsletters")
