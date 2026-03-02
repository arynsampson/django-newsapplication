from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from articles.models import Article
from publishers.models import Publisher

User = get_user_model()


class ArticlesTests(TestCase):
    """
    Test suite for article-related views: creation, editing, deletion, and
    access control.

    Includes tests for:
        1. Creating a new article as a journalist
        2. Editing article details
        3. Deleting an article
        4. Preventing unauthorized users from editing articles
    """

    def setUp(self) -> None:
        """
        Set up initial test data.

        Creates:
            - Two users: one journalist and one reader
            - One publisher linked to the journalist
            - One article authored by the journalist
        """
        # Create a journalist user
        self.user_journalist = User.objects.create_user(
            username="journalist1",
            email="j1@example.com",
            password="password123",
            role="Journalist",
        )

        # Create a reader user
        self.reader = User.objects.create_user(
            username="reader1",
            email="reader@example.com",
            password="password123",
            role="Reader",
        )

        self.publisher_owner = User.objects.create_user(
            username="publisher_owner",
            email="publish_owner@gmail.com",
            password="password123",
            role="Publisher",
        )

        # Create a publisher and link journalist
        self.publisher = Publisher.objects.create(
            name="Test Publisher", description="", owner=self.publisher_owner
        )
        self.publisher.journalists.add(self.user_journalist)

        # Create an article authored by the journalist
        self.article = Article.objects.create(
            title="Test Article",
            content="Some content",
            author=self.user_journalist,
            approved=False,
            published=False,
        )

    def test_create_article(self) -> None:
        """
        Test that a journalist can create a new article.

        - Logs in the journalist
        - Sends a POST request to create_article view
        - Asserts that the article count increases
        - Asserts redirect to home after creation
        """
        self.client.login(username="journalist1", password="password123")
        create_url = reverse("create_article")
        data = {"title": "New Article", "content": "Content here"}
        response = self.client.post(create_url, data)

        # Check that a new article was created
        self.assertEqual(Article.objects.count(), 2)
        self.assertRedirects(response, reverse("home"))

    def test_edit_details_of_article(self) -> None:
        """
        Test that a journalist can edit details of their article.

        - Logs in the journalist
        - Sends POST request to edit_article view with 'update' action
        - Verifies that article content is updated and approved flag reset
        """
        self.client.login(username="journalist1", password="password123")
        edit_url = reverse("edit_article", args=[self.article.pk])
        data = {
            "title": "Updated Article",
            "content": "Updated content",
            "action": "update",
        }
        response = self.client.post(edit_url, data)

        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated Article")
        self.assertFalse(self.article.approved)

    def test_delete_an_article(self) -> None:
        """
        Test that a journalist/editor can delete their article.

        - Logs in the journalist
        - Sends GET request to delete_article view
        - Asserts the article is removed from database
        - Verifies redirect to home
        """
        self.client.login(username="journalist1", password="password123")
        delete_url = reverse("delete_article", args=[self.article.pk])
        response = self.client.get(delete_url)

        # Check that the article no longer exists
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())
        self.assertRedirects(response, reverse("home"))

    def test_unauthorized_edit_article_access(self) -> None:
        """
        Test that a user who is not author/reviewer/publisher
        cannot edit the article.

        - Logs in as a reader
        - Sends GET request to edit_article view
        - Asserts user is redirected to home
        """
        self.client.login(username="reader1", password="password123")
        edit_url = reverse("edit_article", args=[self.article.pk])
        response = self.client.get(edit_url)

        self.assertRedirects(response, reverse("home"))
