from django import forms

from .models import Publisher


class PublisherForm(forms.ModelForm):
    """
    Form for updating a Publisher instance.

    This form exposes the following fields for user input:

        - name: The publisher's name.
        - description: A brief description or summary of the publisher.
    """

    class Meta:
        model = Publisher
        fields = ["name", "description"]
