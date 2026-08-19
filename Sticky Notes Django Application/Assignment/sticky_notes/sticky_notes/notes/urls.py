from django.urls import path
from .views import (
    view_all_notes,
    view_note,
    create_note,
    update_note,
    delete_note,
)

urlpatterns = [
    # URL pattern for displaying a list of all notes
    path("", view_all_notes, name="view_all_notes"),

    # URL pattern for displaying details of a specific note
    path("note/<int:pk>/", view_note, name="view_note"),

    # URL pattern for creating a new note
    path("note/new/", create_note, name="create_note"),

    # URL pattern for updating an existing note
    path("note/<int:pk>/edit/", update_note, name="update_note"),

    # URL pattern for deleting an existing note
    path("note/<int:pk>/delete/", delete_note, name="delete_note"),
]

