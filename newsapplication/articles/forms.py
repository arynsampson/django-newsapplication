from django import forms
from django.contrib.auth import get_user_model

from .models import Article


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing :class:`Article` instances.

    This form:
        - Allows a Journalist or Editor to create/update an article.
        - Allows optional assignment of an Editor as reviewer.
        - Restricts reviewer choices to users with role="Editor".

    Fields:
        - title (str): The title of the article.
        - content (str): The body content of the article.
        - reviewer (User, optional): An Editor assigned to review the article.

    Notes:
        - The reviewer field dynamically filters users by role.
        - `required=False` allows articles to be saved without an
        assigned reviewer.
    """

    # Retrieve the active custom User model
    User = get_user_model()

    # Reviewer must be of role "Editor"
    reviewer = forms.ModelChoiceField(
        queryset=User.objects.filter(role="Editor"),
        required=False,
        empty_label="Select Reviewer",
    )

    class Meta:
        model = Article
        fields = ["title", "content", "reviewer"]
