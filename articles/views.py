from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from MySQLdb import DatabaseError

from core.decorators import journalist_editor_required, journalist_required
from publishers.models import Publisher

from .forms import ArticleForm
from .models import Article


@login_required
@journalist_required
def create_article(request: HttpRequest) -> HttpResponse:
    """
    View for creating a new article by a journalist.

    Only accessible to authenticated users with the journalist role. Handles
    both GET and POST requests:

    - GET: displays an empty ArticleForm for the journalist to fill out.
    - POST: validates the submitted ArticleForm, assigns the current user as
        the author, saves the article to the database, and redirects to home.

    Notes:
        - Uses `login_required` to ensure the user is authenticated.
        - Uses `journalist_required` to ensure the user has
            journalist permissions.
        - `form.save(commit=False)` is used to add the author before saving.
        - Redirects to 'home' after a successful submission.
        - On GET or invalid form, re-renders the form template
            with validation errors.

    :param request: The HTTP request object containing GET or POST data
    :type request: HttpRequest
    :return: HttpResponse object rendering the article creation template or
             redirecting to home
    :rtype: HttpResponse

    """
    if request.method == "POST":
        form: ArticleForm = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect("home")
    else:
        form = ArticleForm()

    return render(
        request,
        "articles/create_article.html",
        {
            "form": form,
        },
    )


@login_required
def view_article(request: HttpResponse, pk: int) -> HttpResponse:
    """
    View an article with access control based on article publish status.

    - Authenticated users can view the article if it is published.
    - Unpublished articles can be viewed only by non-Readers:

    Notes:
        - Uses `get_object_or_404` to retrieve the article by primary key.
        - Template receives the article, associated newsletters,
            and the current user.

    :param request: The HTTP request object containing GET data
    :type request: HttpRequest
    :param pk: Primary key of the article to view
    :type pk: int
    :return: HttpResponse rendering the article template or
        redirecting to home
    :rtype: HttpResponse

    """
    article = get_object_or_404(Article, pk=pk)
    user = request.user

    if not article.approved and user.role == "Reader":
        return redirect("home")

    return render(
        request,
        "articles/article.html",
        {
            "article": article,
            "newsletters": article.newsletters.all(),
            "user": user,
        },
    )


@login_required
@journalist_editor_required
def edit_article(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Edit an article based on user permissions and requested action.

    Only accessible to authenticated users with journalist or
    editor permissions.
    Handles GET and POST requests with multiple possible POST actions:

    POST actions:
        - "update": Update the article content. Marks article as not approved.
        - "approve": Approve the article.
        - "j-publish": Publish the article as a journalist (only if approved).
        - "p-publish": Publish the article as a publisher
            (requires publisher_id).

    Access control:
        - Users can only edit unpublished articles if
            they are the author or reviewer.
        - Users cannot edit already published articles unless
            allowed by action.

    Notes:
        - Uses `get_object_or_404` to fetch the article.
        - Retrieves the publishers associated with the current journalist.
        - Redirects are used to enforce access control and after actions.

    :param request: The HTTP request object containing GET or POST data
    :type request: HttpRequest
    :param pk: Primary key of the article to edit
    :type pk: int
    :return: HttpResponse rendering the edit template or redirecting
        to another page
    :rtype: HttpResponse

    """
    article = get_object_or_404(Article, pk=pk)
    user = request.user
    # Gets all the Publishers that the requesting user belongs to
    journalist_publishers = Publisher.objects.filter(journalists=user)

    if not article.approved and user.role == "Reader":
        return redirect("home")

    if request.method == "POST":
        action = request.POST.get("action")

        # Edit Article title, description, or reviewer
        if action == "update":
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                try:
                    updated_article = form.save(commit=False)
                    updated_article.approved = False
                    updated_article.save()
                except DatabaseError as e:
                    return HttpResponse(f"Error: {e}")

        # Editor approves the article
        elif action == "approve":
            article.approved = True

        # Article is published by the journalist
        elif action == "j-publish":
            if article.approved:
                article.published = True
                article.published_by = user
            else:
                return redirect("edit_article")

        # Article is published by the publisher
        elif action == "p-publish":
            publisher_id = request.POST.get("publisher_id")

            if not request.POST.get("publisher_id"):
                return redirect("edit_article", pk=pk)

            publisher_chosen = Publisher.objects.filter(
                id=publisher_id, journalists=request.user
            ).first()

            article.published = True
            article.publisher = publisher_chosen
            article.published_by = request.user
            article.save()

        article.save()

        return redirect("view_article", pk=pk)
    else:
        form = ArticleForm(instance=article)
        return render(
            request,
            "articles/edit_article.html",
            {
                "article": article,
                "form": form,
                "user": user,
                "journalist_publishers": journalist_publishers,
            },
        )


@login_required
@journalist_editor_required
def delete_article(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Delete an article identified by its primary key.

    Only accessible to users with journalist or editor permissions.
    Retrieves the article by primary key and deletes it from the database,
    then redirects to the home page.

    Notes:
        - Uses `get_object_or_404` to fetch the article;
            raises 404 if not found.
        - Optional: Wrap `article.delete()` in try/except to catch
            `DatabaseError` or `IntegrityError` if there is a problem
                with deletion.
        - Redirects to 'home' after successful deletion.

    :param request: The HTTP request object
    :type request: HttpRequest
    :param pk: Primary key of the article to delete
    :type pk: int
    :return: HttpResponse redirecting to the home page
    :rtype: HttpResponse

    """
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return redirect("home")
