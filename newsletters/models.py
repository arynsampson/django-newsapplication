from django.conf import settings
from django.db import models

from articles.models import Article

# # Create your models here.


class Newsletter(models.Model):
    """
    Represents a newsletter containing a collection of articles.

    A Newsletter is authored by a journalist or editor and
    can be associated with multiple articles.

    Relationships:
        - author: The user who created the newsletter.
        - articles: Articles included in this newsletter.

    Notes:
        - `created_at` automatically records when the newsletter was created.
    """

    title = models.CharField(max_length=50)
    description = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_newsletter",
    )
    articles = models.ManyToManyField(Article, related_name="newsletters")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)
