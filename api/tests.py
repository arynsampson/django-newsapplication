from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article
from newsletters.models import Newsletter
from publishers.models import Publisher

User = get_user_model()


class APITests(APITestCase):
    """
    API test suite for the newsapplication.

    Covers:
    - Article creation by journalists
    - Article approval and deletion by editors
    - Newsletter-article addition
    - Permissions enforcement for readers
    - Reader subscription articles
    - Email notifications via signals
    """

    def setUp(self):
        """
        Setup test users, publisher, articles, and newsletter.

        Creates:
        - A reader, editor, journalist, and publisher owner
        - A publisher instance
        - Two articles
        - A newsletter
        """
        self.reader = User.objects.create_user(
            username="reader",
            password="reader_pass",
            email="reader@gmail.com",
            role="Reader",
        )
        self.editor = User.objects.create_user(
            username="editor", password="editor_pass", role="Editor"
        )
        self.journalist = User.objects.create_user(
            username="journalist",
            password="journalist_pass",
            role="Journalist",
        )
        self.publisher_owner = User.objects.create_user(
            username="publisher_owner",
            password="publisher_owner_pass",
            role="Publisher",
        )
        self.publisher = Publisher.objects.create(
            name="Publisher", description="", owner=self.publisher_owner
        )

        self.article1 = Article.objects.create(
            title="Set up Article",
            content="More content!",
            author=self.journalist,
            reviewer=self.editor,
        )

        self.article2 = Article.objects.create(
            title="Second Set up Article",
            content="EVEN More content!",
            author=self.journalist,
            reviewer=self.editor,
        )

        self.newsletter1 = Newsletter.objects.create(
            title="Newsletter test",
            description="newsletter testing",
            author=self.journalist,
        )

    def test_journalist_can_create_articles(self):
        """
        Test that a journalist can create a new article via the API.

        Expects HTTP 201 CREATED on successful submission.
        """
        self.client.force_authenticate(user=self.journalist)
        url = reverse("api_create_article")

        payload = {
            "title": "Article from test",
            "content": "blah blah blah",
            "author": self.journalist.pk,
        }

        response = self.client.post(
            url,
            payload,
        )
        self.assertEqual(response.status_code, 201)

    def test_editor_can_approve_article(self):
        """
        Test that an editor can approve an article by
        updating the 'approved' field.

        Expects HTTP 200 OK on successful update.
        """
        self.client.force_authenticate(user=self.editor)
        url = reverse("api-article_update", kwargs={"pk": self.article1.pk})

        payload = {"approved": True}

        response = self.client.put(
            url,
            payload,
        )
        self.assertEqual(response.status_code, 200)

    def test_editor_can_delete_article(self):
        """
        Test that an editor can delete an article.

        Expects HTTP 200 OK on successful deletion.
        """
        self.client.force_authenticate(user=self.editor)
        url = reverse("api_delete_article", kwargs={"pk": self.article1.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)

    def test_add_article_to_newsletter(self):
        """
        Test adding an article to a newsletter.

        Verifies that the article count in the newsletter increases.
        """
        self.newsletter1.articles.add(self.article1)

        self.assertEqual(self.newsletter1.articles.count(), 1)

    def test_reader_cannot_create_article(self):
        """
        Test that a reader cannot create an article.

        Expects HTTP 403 FORBIDDEN as readers are not
        allowed to create articles.
        """
        self.client.force_authenticate(user=self.reader)
        url = reverse("api_create_article")

        payload = {
            "title": "Article from test",
            "content": "blah blah blah",
            "author": self.journalist.pk,
        }

        response = self.client.post(
            url,
            payload,
        )

        self.assertEqual(response.status_code, 403)

    def test_reader_retrieve_subscribed_content(self):
        """
        Test that a reader can retrieve articles from their
        subscribed journalists
        and publishers.

        - Marks article1 as published.
        - Subscribes reader to a journalist and publisher.
        - Expects HTTP 200 OK with articles returned.
        """
        self.client.force_authenticate(user=self.reader)
        url = reverse("api-subscriber_articles")

        self.reader.subscribed_journalists.add(self.journalist)
        self.reader.reader_publishers.add(self.publisher)

        self.article1.published = True

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_signal_sending_email_to_subscribers(self):
        """
        Test that the signal sends an email when an article is published.

        - Ensures that only subscribed readers receive notifications.
        """
        self.client.force_authenticate(user=self.reader)
        self.reader.subscribed_journalists.add(self.journalist)

        mail.outbox = []
        self.article2.published = True
        self.article2.save()

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        self.assertIn(self.article2.title, sent_email.subject)
        self.assertIn(self.article2.content, sent_email.body)
        self.assertIn(self.reader.email, sent_email.to)
