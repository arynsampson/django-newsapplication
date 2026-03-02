from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    """
    Form for registering a new user with email and role.

    Attributes:
        email (EmailField): The user's email address, required and unique.
        role (ChoiceField): The user's role, either 'Vendor' or 'Buyer'.
    """

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        required=True,
        choices=[
            ("Reader", "Reader"),
            ("Editor", "Editor"),
            ("Journalist", "Journalist"),
            ("Publisher", "Publisher"),
        ],
    )

    class Meta:
        """
        Metadata for the registration form.

        Attributes:
            model (User): The user model to create.
            fields (list): Fields included in the form: username, email,
            password1, password2, role.
        """

        model = get_user_model()
        fields = ["username", "email", "password1", "password2", "role"]

    def clean_email(self):
        """
        Ensure the email address is unique across all users.

        Returns:
            str: Cleaned email address.
        """
        User = get_user_model()
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this" "email already exists."
            )
        return email

    def save(self, commit=True):
        """
        Save the new user instance with the provided email.

        Args:
            commit (bool): Whether to save the instance to the database.

        Returns:
            User: The saved user instance.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
