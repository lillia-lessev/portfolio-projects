from django.db import models


# Create your models here.
class Note(models.Model):
    """
    Model representing a Sticky Note.

    Fields:
        - title: CharField for the note title with a maximum length of 255 characters.
        - content: TextField for the note content.
        - date_created: DateTimeField set to the current date and time when the note is created.

    Relationships:
        - user: ForeignKey representing the user who created the note

    Methods:
        - __str__: Returns a string representation of the note, showing the title.

    :param models.Model: Django's base model class.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    # Define a ForeignKey for the user's relationship
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, null=True, blank=True # ensures that if a user is deleted, all corresponding notes will also be removed, maintaining data integrity
    )

    def __str__(self):
        # note_str = self.title + self.content
        return self.title


class User(models.Model):
    """
    Model representing the user who created a sticky note

    Fields:
        - name: CharField for the user's name.

    Methods:
        - __str__: Returns a string representation of the user, showing the name

    :param models.Model: Django's base model class.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
