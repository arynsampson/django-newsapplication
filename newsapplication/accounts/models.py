from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):

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
