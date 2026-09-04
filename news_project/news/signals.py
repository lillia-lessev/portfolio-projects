"""
Signals that run when an Article is approved

    - Email all relevant subscribers
    - POST the approved article to /api/approved/
"""
import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


from .models import Article

# create logger object to write log messages for errors etc.
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, **kwargs):
    """
    Triggered after Article is saved.

    If Article is approved:
        - Set approved_at timestamp
        - Email all subscribers of journalist / publisher
        - POST the article data to internal /api/approved/ endpoint
    """

    # Only run when article is approved and hasn't already been processed
    if (not instance.approved) or (instance.approved_at is not None):
        return None
    else:
        # Update approved_at timestamp
        Article.objects.filter(
            pk=instance.pk
        ).update(approved_at=timezone.now())

        # Gather subscriber emails
        emails = set()

        if instance.publisher:
            for subscriber in instance.publisher.publisher_subscribers.all():
                if subscriber.email:
                    emails.add(subscriber.email)

        for subscriber in instance.author.journalist_subscribers.all():
            if subscriber.email:
                emails.add(subscriber.email)

        # Send email
        if emails:
            send_mail(
                subject=f"New approved article: {instance.title}",
                message=instance.content[:500] + "...",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(emails),
                fail_silently=True,
            )

        # POST to API endpoint
        try:
            requests.post(
                'http://127.0.0.1:8000/api/approved',
                json={
                    'id': instance.id,
                    'title': instance.title,
                    'author': instance.author.username,
                    'publisher': instance.publisher.name if instance.publisher else None,
                },
                timeout=5,
            )
        except Exception as e:
            logger.error(f"Failed to post approved article"
                         + f" (ID: {instance.id}) to /api/approved/: {e}")
