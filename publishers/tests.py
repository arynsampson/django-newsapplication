from django.contrib.auth import get_user_model
from django.test import TestCase

from publishers.models import Publisher

User = get_user_model()


class PublisherTests(TestCase):
    """
    Unit tests for the Publisher model.

    These tests verify that users of different roles can be properly added
    to a Publisher instance and that the ManyToMany relationships function
    as expected.
    """

    def setUp(self) -> None:
        """
        Set up test data for the Publisher tests.

        - Creates a Publisher instance.
        - Creates one journalist user.
        - Creates one reader user.
        """

        # Create a user to own the Publisher
        self.publisher_owner = User.objects.create_user(
            username="publisher_owner",
            email="publisher_owner@example.com",
            password="password123",
            role="Publisher",
        )
        # Create a publisher
        self.publisher = Publisher.objects.create(
            name="Test Publisher", description="", owner=self.publisher_owner
        )

        # Create a journalist user
        self.user_journalist = User.objects.create_user(
            username="journalist1",
            email="j1@example.com",
            password="password123",
            role="Journalist",
        )

        # Create a reader user
        self.user_reader = User.objects.create_user(
            username="reader1",
            email="reader@example.com",
            password="password123",
            role="Reader",
        )

    def test_add_users_to_publisher(self) -> None:
        """
        Test that users of different roles can be added to a Publisher.

        Steps:
        1. Add a journalist to the publisher.journalists ManyToMany field.
        2. Add a reader to the publisher.readers ManyToMany field.
        3. Retrieve the publisher from the database.
        4. Assert that the counts for journalists and readers are correct.
        """

        # Add users to Publisher
        self.publisher.journalists.add(self.user_journalist)
        self.publisher.readers.add(self.user_reader)

        publisher = Publisher.objects.get(pk=self.publisher.pk)

        self.assertEqual(publisher.journalists.count(), 1)
        self.assertEqual(publisher.readers.count(), 1)
