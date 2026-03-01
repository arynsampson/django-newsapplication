from django.conf import settings
from django.db import models


# Create your models here.
class Publisher(models.Model):
    """
    Represents a publishing organization within the platform.

    A Publisher acts as a collaborative entity that connects:

        - Journalists (content creators)
        - Editors (content reviewers)
        - Readers (subscribers)

    Relationships:
        - journalists → Users with role="Journalist"
        - editors → Users with role="Editor"
        - readers → Users with role="Reader"

    Notes:
        - Role restrictions are enforced via ``limit_choices_to``.
        - All relationships are optional (blank=True).
        - Articles published through a Publisher reference this model
          via a ForeignKey (see Article.publisher).
    """

    name = models.CharField(max_length=255)
    description = models.TextField(default="Description TBA")

    # Owner: the user who created/owns this publisher
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_publisher",
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        # user.journalist_publishers is the publishers the journalist exists in
        related_name="journalist_publishers",
        blank=True,
        limit_choices_to={"role": "Journalist"},
    )

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        # user.editor_publishers is the publishers the editor exists in
        related_name="editor_publishers",
        blank=True,
        limit_choices_to={"role": "Editor"},
    )

    readers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        # user.reader_publishers is the publishers the reader exists in
        related_name="reader_publishers",
        blank=True,
        limit_choices_to={"role": "Reader"},
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
