from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from articles.models import Article

from .serializers import ArticleSerializer

User = get_user_model()


# Create your views here.
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def articles(request):
    """
    Retrieve all published articles.

    Authentication:
        - JWTAuthentication required.

    Method:
        - GET only.

    Returns:
        - 200 OK with serialized list of published articles.
    """
    articles = Article.objects.filter(published=True)
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def article(request, pk):
    """
    Retrieve a single article by primary key.

    Authentication:
        - JWTAuthentication required.

    :param pk: Primary key of the article.
    :return: Serialized article data or 404 if not found.
    """
    article = get_object_or_404(Article, pk=pk)
    serializer = ArticleSerializer(article)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
def article_create(request):
    """
    Create a new article.

    Rules:
        - Only users with role "Journalist" may create articles.
        - Journalists cannot create articles on behalf of others.
        - The provided author must also have role "Journalist".

    Method:
        - POST only.

    Returns:
        - 201 CREATED on success.
        - 400 BAD REQUEST for validation errors.
        - 403 FORBIDDEN for permission violations.
    """

    if request.method == "POST":

        if request.user.role != "Journalist":
            return Response(
                {"error": "User cannot perform this operation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        article_author = get_object_or_404(User, pk=request.data.get("author"))

        if request.user != article_author:
            return Response(
                {"error": "Articles cannot be made on behalf of journalists."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if article_author.role != "Journalist":
            return Response(
                {"error": "Chosen author cannot perform this operation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            serializer = ArticleSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
def article_delete(request, pk):
    """
    Delete an article.

    Rules:
        - Only users with role "Journalist" and "Editor" may delete articles.
        - An article may only be deleted by its author.

    :param pk: Primary key of the article to delete.
    :return:
        - 200 OK if deleted.
        - 403 FORBIDDEN if permission denied.
        - 404 NOT FOUND if article does not exist.
    """

    if request.user.role not in ["Journalist", "Editor"]:
        return Response(
            {"error": "User cannot perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )

    article = Article.objects.get(pk=pk)

    if request.user != article.author and request.user.role != "Editor":
        return Response(
            {"error": "User cannot perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )

    article.delete()
    return Response(
        {"error": "Article has been deleted."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def subscriber_articles(request):
    """
    Retrieve published articles from a reader's subscriptions.

    This endpoint returns articles that:

        - Are marked as published.
        - Are authored by journalists the reader subscribes to.
        - OR are published by publishers the reader subscribes to.

    Access Rules:
        - Only users with role "Reader" may access this endpoint.
        - The reader must exist in the system.

    Response Codes:
        - 200 OK: Successfully returns serialized articles.
        - 403 FORBIDDEN: If the requesting user is not a Reader.
        - 404 NOT FOUND: If the reader has no subscriptions.

    :param request: The HTTP request object.
    :param pk: Primary key of the reader whose subscriptions are being queried.
    :return: JSON response containing serialized articles or error message.
    """
    reader_user_requested = request.user

    if reader_user_requested.role != "Reader":
        return Response(
            {"error": "User cannot perform this operation."},
            status=status.HTTP_403_FORBIDDEN,
        )

    subscribed_journalists = reader_user_requested.subscribed_journalists.all()

    subscribed_publishers = reader_user_requested.reader_publishers.all()

    articles = (
        Article.objects.filter(published=True)
        .filter(
            Q(author__in=subscribed_journalists)
            | Q(publisher__in=subscribed_publishers)
        )
        .distinct()
    )

    # If reader has no subscriptions at all
    if (
        not subscribed_journalists.exists()
        and not subscribed_publishers.exists()
    ):
        return Response(
            {"message": "Reader has no subscriptions."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ArticleSerializer(articles, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
def article_update(request, pk):
    """
    Update an existing article.

    Permissions:
    - User must be authenticated.
    - Only a Journalist and Editor may update the article.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): Primary key of the article to update.

    Returns:
        Response:
            - 200 OK with updated article data.
            - 403 Forbidden if user is not the author.
            - 404 Not Found if article does not exist.
            - 400 Bad Request if validation fails.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role in ["Reader", "Publisher"]:
        return Response(
            {"error": "You do not have permission to update this article."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.data.get("approved"):
        if request.user != article.reviewer:
            return Response(
                {
                    "error": "You do not have permission to"
                    "approve this article."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            article.approved = bool(request.data.get("approved"))

    serializer = ArticleSerializer(
        article,
        data=request.data,
        partial=True,
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
