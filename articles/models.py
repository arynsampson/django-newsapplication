from django.conf import settings
from django.db import models

from publishers.models import Publisher


# Create your models here.
class Article(models.Model):
    """
    Represents a news article authored by a Journalist.

    An Article lifecycle:
        1. Created by an author (Journalist).
        2. Optionally assigned to a reviewer (Editor).
        3. Approved by reviewer.
        4. Published either:
            - Independently by a Journalist, or
            - Through a Publisher.

    Relationships:
        - author → User (Journalist)
        - reviewer → User (Editor, optional)
        - published_by → User (who executed publishing action)
        - publisher → Publisher (optional organizational publisher)

    Flags:
        - approved (bool): Indicates if the article has passed review.
        - published (bool): Indicates if the article is publicly visible.

    Timestamps:
        - created_at: Automatically set when the article is created.
    """

    title = models.CharField(max_length=50)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_articles",
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approved_articles",
    )

    # This refers to
    #   - the journalist that clicks the publish button
    #   - if the Article was independetly published, this value will be
    #   - displayed on the Article model instance published_by value
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="published_articles",
    )

    # This field is used for when an Article is published by a Publisher,
    # the Publishers name will be displayed on the
    # Article model instance publisher value
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    approved = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)
