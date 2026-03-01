from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTests(TestCase):
    """
    Test suite for authentication-related views: register, login, logout, and
    password reset (forgot password).

    Tests included:
        1. User can register as a Reader.
        2. User can logout.
        3. An unauthenticated user cannot login.
        4. Forgot password functionality sends an email.
    """

    def test_register_reader(self):
        """
        Test that a user can register successfully as a Reader.

        Sends a POST request to the 'register' view with a username,
        email, password, and role='Reader'. Verifies that a new user is
        created.
        """
        register_url = reverse("register")
        data = {
            "username": "test_reader",
            "email": "reader@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "role": "Reader",
        }

        # Send POST request to register the user
        response = self.client.post(register_url, data)

        # Fetch the newly created user from the database
        user_exists = User.objects.filter(username="test_reader").exists()

        # Assert that the user was created
        self.assertTrue(user_exists, "User should be created in the database.")

    def test_logout_user(self):
        """
        Test that a logged-in user can logout successfully.

        - Creates a test user and logs them in.
        - Sends a GET request to the 'logout' view.
        - Verifies that the user session is cleared.
        """
        # Create and log in a test user
        user = User.objects.create_user(
            username="logout_user", password="password123"
        )
        self.client.login(username="logout_user", password="password123")

        # Send GET request to logout
        logout_url = reverse("logout")
        response = self.client.get(logout_url)

        # Assert that the response redirects to login page
        self.assertRedirects(response, reverse("login"))

        # Assert that user is logged out
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "User should be logged out.",
        )

    def test_unauthenticated_user_cannot_login(self):
        """
        Test that an unauthenticated user cannot login with invalid
        credentials.

        - Sends a POST request to the login view with incorrect
        username/password.
        - Asserts that the user is not authenticated.
        - Asserts that the login page is returned (status code 200).
        """
        login_url = reverse("login")
        data = {
            "username": "nonexistent_user",
            "password": "wrongpassword",
        }

        response = self.client.post(login_url, data)

        # Assert user is not authenticated
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "User should not be logged in.",
        )

        # Assert the response status code is 200 (login page redisplayed)
        self.assertEqual(response.status_code, 200)

        # Assert the login form is in the context
        self.assertIn("form", response.context)

    def test_forgot_password_sends_email(self):
        """
        Test the forgot password functionality.

        - Creates a test user with an email.
        - Sends a POST request to the password reset view.
        - Verifies that an email is sent to the user's email address.
        """
        # Create a test user with email
        user = User.objects.create_user(
            username="forgot_user",
            email="forgot@example.com",
            password="password123",
        )

        # Send POST request to password reset view
        reset_url = reverse("password_reset")
        data = {"email": "forgot@example.com"}
        response = self.client.post(reset_url, data)

        # Assert redirect to password reset done page
        self.assertRedirects(response, reverse("password_reset_done"))

        # Assert that an email was sent
        self.assertEqual(
            len(mail.outbox), 1, "One password reset email should be sent."
        )
        self.assertIn("forgot@example.com", mail.outbox[0].to)
