from django.shortcuts import render, get_object_or_404, redirect
from .models import Note
from .forms import NoteForm

# Create your views here.
def view_all_notes(request):
    """
    View to display a list of all notes.

    :param request: HTTP request object.
    :return: Rendered template with a list of notes.
    """
    notes = Note.objects.all()

    # Creating a context dictionary to pass data
    context = {
        "notes": notes, 
        "page_title": "All Sticky Notes",
    }
    return render(request, "notes/view_all_notes.html", context)


def view_note(request, pk):
    """
    View to display details of a specific note.

    :param request: HTTP request object. 
    :param pk: Primary key of the note.

    :return: Rendered template with details of the specified post.
    """
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/view_note.html", {"note": note})

def create_note(request):
    """
    View to create a new note.

    :param request: HTTP request object.
    :return: Rendered template for creating a new note.
    """
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.save()
            return redirect("view_all_notes")
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form})

def update_note(request, pk):
    """
    View to update an existing note.

    :param request: HTTP request object.
    :param pk: Primary key of the note to be updated.
    :return: Rendered template for updating the specified note.

    """
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            note.save()
            return redirect("view_all_notes")
    else:
        form = NoteForm(instance=note)
    
    return render(request, "notes/note_form.html", {"form": form})


def delete_note(request, pk):
    """
    View to delete an existing note.
    :param request: HTTP request object.
    :param pk: Primary key of the note to be deleted.
    :return: Redirect to the note list after deletion.
    """
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect("view_all_notes")
