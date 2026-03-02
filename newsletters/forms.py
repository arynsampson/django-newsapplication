from django import forms

from .models import Newsletter


class NewsletterForm(forms.ModelForm):
    """
    Form for creating or updating a Newsletter instance.

    This form exposes the following fields for user input:

        - title: The newsletter's title.
        - description: A brief description or summary of the newsletter.
    """

    class Meta:
        model = Newsletter
        fields = ["title", "description"]
