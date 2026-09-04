"""
Models for the News Application

CustomUser, Publisher, Article, Newsletter

Different roles have different permissions and relationships.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    """
    Represents custom user model that extends AbstractUser

    Users' roles can be: reader, editor, journalist.

    Reader - Can only view articles and newsletters.
    Editor - Can view, update, and delete articles and newsletters.
    Journalist - Can create, view, update, and delete articles and newsletters.
    """

    email = models.EmailField(
        'email',
        unique=True,
        help_text=("Each email address may only"
                   + " be used to register one user account.")
    )

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'editor'),
        ('journalist', 'Journalist'),
        ('publisher', 'Publisher'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader',
        help_text="User's role in the system"

    )

    # READER fields
    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        blank=True,
        related_name='publisher_subscribers',
        help_text="Publishers this reader is subscribed to."
    )

    subscribed_journalists = models.ManyToManyField(
            'self',
            blank=True,
            symmetrical=False,  # Not a mutual relationship.
            related_name='journalist_subscribers',
            help_text="Journalists this reader is subscribed to."
        )

    def get_publisher(self):
        """Get publisher if user belongs to one"""
        if self.role == 'journalist':
            return self.publisher_journalists.first()
        if self.role == 'editor':
            return self.publisher_editors.first()
        if self.role == 'publisher':
            return self.publisher_owner.first()

    def __str__(self):
        """Returns string representation of user."""
        return f"{self.username} ({self.role})"

    class Meta:
        """Meta"""
        verbose_name = "User"
        verbose_name_plural = "Users"


class Publisher(models.Model):
    """
    Represents a publisher which can have multiple editors & journalists.
    """

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='publisher_owner',
        limit_choices_to={'role': 'publisher'}
    )

    editors = models.ManyToManyField(
        CustomUser,
        related_name='publisher_editors',
        blank=True,
        limit_choices_to={'role': 'editor'},
        help_text="Editors affiliated with this publisher."
    )

    journalists = models.ManyToManyField(
        CustomUser,
        related_name='publisher_journalists',
        blank=True,
        limit_choices_to={'role': 'journalist'},
        help_text="Journalists affiliated with this publisher."
    )

    def __str__(self):
        """Return publisher name"""
        return self.name


@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    # Group users into Django group according to role
    role_to_group = {
        'reader': 'Reader',
        'journalist': 'Journalist',
        'publisher': 'Publisher',
        'editor': 'Editor',
    }
    group_name = role_to_group.get(instance.role)
    if not group_name:
        return None

    group, _ = Group.objects.get_or_create(name=group_name)
    instance.groups.clear()
    instance.groups.add(group)


class Article(models.Model):
    """
    Represents a news article written by a specific journalist.

    An article is associated with a journalist (for independent articles)
      and also optionally a publisher (for publisher content).
    """

    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='articles',
        limit_choices_to={'role': 'journalist'},
        help_text="Journalist who wrote the article."
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        help_text="Optional publisher of the article."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(
        default=False,
        help_text="Whether the article has been approved by an editor."
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when article was approved."
    )

    def __str__(self):
        """Returns the article title"""
        return self.title

    class Meta:
        """Meta"""
        ordering = ['-created_at']


class Newsletter(models.Model):
    """
    Curated collection of articles created by journalists
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='newsletters',
        limit_choices_to={'role': 'journalist'},
        help_text="Journalist who created the newsletter."
    )

    articles = models.ManyToManyField(
        Article,
        related_name='newsletters',
        blank=True,
        help_text='Articles included in this newsletter.'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns newsletter title"""
        return self.title
