from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from articles.models import Article
from newsletters.models import Newsletter


def assign_user_role_and_permissions(user):
    """
    Assigns a user to the correct group based on their role
    and ensures the group has the correct permissions.
    """

    role = user.role

    # Clear existing groups
    user.groups.clear()

    # Get or create group
    group, created = Group.objects.get_or_create(name=role)

    # Clear permissions before assigning to prevent duplicates
    group.permissions.clear()

    # Get content types
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    permissions = []

    # READER PERMISSIONS
    if role == "Reader":
        permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct],
            codename__in=[
                "view_article",
                "view_newsletter",
            ],
        )

    # EDITOR PERMISSIONS
    elif role == "Editor":
        permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct],
            codename__in=[
                "view_article",
                "change_article",
                "delete_article",
                "create_newsletter",
                "view_newsletter",
                "change_newsletter",
                "delete_newsletter",
            ],
        )

    # JOURNALIST PERMISSIONS
    elif role == "Journalist":
        permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct],
            codename__in=[
                "add_article",
                "view_article",
                "change_article",
                "delete_article",
                "add_newsletter",
                "view_newsletter",
                "change_newsletter",
                "delete_newsletter",
            ],
        )

    # Assign permissions to group
    group.permissions.set(permissions)

    # Add user to group
    user.groups.add(group)

    return user
