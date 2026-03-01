from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from articles.models import Article
from newsletters.models import Newsletter

User = get_user_model()


class NewsletterTests(TestCase):
    """
    Tests for Newsletter functionality.

    Covers:
        - Newsletter creation by journalists.
        - Only the newsletter creator can add or remove articles.
    """

    def setUp(self) -> None:
        """
        Create test data:

        - One journalist user (newsletter creator)
        - One other journalist user
        - Two  articles
        """
        # Create journalist users
        self.journalist_author = User.objects.create_user(
            username="journo-one",
            email="journo-one@example.com",
            password="password123",
            role="Journalist",
        )
        self.other_journalist = User.objects.create_user(
            username="other-journalist",
            email="other-journalist@example.com",
            password="password123",
            role="Journalist",
        )

        self.reader = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="password123",
            role="Reader",
        )

        # Create articles
        self.article1 = Article.objects.create(
            title="Article 1",
            content="Content 1 blh blh",
            author=self.journalist_author,
        )
        self.article2 = Article.objects.create(
            title="Article 2",
            content="Content 2 yuh yuh",
            author=self.other_journalist,
        )

    def test_journalist_can_create_newsletter(self) -> None:
        """
        Test that a journalist can successfully create anewsletter via POST request.

        Steps:
            1. Log in as the creator journalist.
            2. Submit POST request with newsletter title and description.
            3. Verify that newsletter count increases.
            4. Verify that newsletter author is set correctly.
            5. Verify redirect after creation.
        """
        self.client.login(username="journo-one", password="password123")
        url = reverse("create_newsletter")
        data = {"title": "News update", "description": "Summary of news"}
        response = self.client.post(url, data)

        # There should now be exactly one newsletter
        self.assertEqual(Newsletter.objects.count(), 1)

        newsletter = Newsletter.objects.first()
        self.assertEqual(newsletter.author, self.journalist_author)
        self.assertEqual(newsletter.title, "News update")
        self.assertRedirects(response, reverse("newsletters"))

    def test_reader_cannot_create_newsletter(self) -> None:
        """
        Test that a reader cannot create anewsletter via POST request.

        Steps:
            1. Log in as the creator reader.
            2. Submit POST request with newsletter title and description.
            3. Verify that newsletter count increases.
            4. Verify that newsletter author is set correctly.
            5. Verify redirect after creation.
        """
        self.client.login(username="reader", password="password123")
        url = reverse("create_newsletter")
        data = {"title": "Reader News update",
                "description": "Blocked"}
        response = self.client.post(url, data)

        # Reader will be redirected as they cannot create newsletters
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_articles_can_be_added_to_newsletters(self) -> None:
        """
        Test that articles can be added to a newsletter successfully.

        This test directly adds an article to the newsletter's ManyToMany
        `articles` field and verifies that the article appears
        in the queryset.

        Steps:
            1. Create a newsletter authored by a journalist.
            2. Add an article to the newsletter.
            3. Assert that the article is now part of the
            newsletter's articles.

        :returns: None
        """
        newsletter = Newsletter.objects.create(
            title="Creator Newsletter",
            description="Newsletter description",
            author=self.journalist_author,
        )

        newsletter.articles.add(self.article1)
        self.assertIn(self.article1, newsletter.articles.all())
