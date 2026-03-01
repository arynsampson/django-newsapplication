from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Article


@receiver(pre_save, sender=Article)
def send_email_when_published(sender, instance, **kwargs):
    """
    Sends an email when an article is published.
    """

    # If article is being created, skip
    if not instance.pk:
        return

    try:
        old_instance = Article.objects.get(pk=instance.pk)
    except Article.DoesNotExist:
        return

    if not old_instance.published and instance.published:

        recipients = []

        # Independent journalist article
        if instance.author and not instance.publisher:
            subscribers = instance.author.subscribers.all()
            recipients = [user.email for user in subscribers if user.email]

        # Publisher article
        elif instance.publisher:
            readers = instance.publisher.readers.all()
            recipients = [user.email for user in readers if user.email]

        if recipients:
            send_mail(
                subject=f"New Article Published: {instance.title}",
                message=f"{instance.title}\n\n{instance.content[:300]}...",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
