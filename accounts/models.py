from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser class.

    This model represents a user on the system annd introduces
    role-based access control and Journalist subscription functionality.
    The subscription functionality involves Reader users "subscribing"
    to Journalist users so that they can receive email notifications
    when Journalists publish articles.
    """
    ROLE_CHOICES = [
        ("Reader", "Reader"),
        ("Journalist", "Journalist"),
        ("Editor", "Editor"),
        ("Publisher", "Publisher"),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="Reader"
    )

    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, related_name="subscribers", blank=True
    )

    def __str__(self) -> str:
        return str(self.username)
