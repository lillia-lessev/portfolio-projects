from django.test import TestCase
from django.urls import reverse
from .models import Note, User

# Create your tests here.
class NoteModelTest(TestCase):
    def setUp(self):
        # Create User object
        user = User.objects.create(name='Test User')
        # Create Note object for testing
        Note.objects.create(title='Test Note', content='Test content for note.', user=user)
    
    def test_note_has_title(self):
        # Test that Note object has title
        note = Note.objects.get(id=1)
        self.assertEqual(note.title, 'Test Note')
    
    def test_note_has_content(self):
        # Test that Note object has content
        note = Note.objects.get(id=1)
        self.assertEqual(note.content, 'Test content for note.')
    
class NoteViewTest(TestCase):
    def setUp(self):
        # Create User object
        user = User.objects.create(name='Test User')
        # Create Note object for testing
        Note.objects.create(title='Test Note', content='Test content for note.', user=user)
        
    def test_view_all_notes(self):
        # Test View All Notes View
        response = self.client.get(reverse('view_all_notes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Note')
    
    def test_view_note(self):
        # Test View Note View
        note = Note.objects.get(id=1)
        response = self.client.get(reverse('view_note', args=[str(note.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Note')
        self.assertContains(response, 'Test content for note.')