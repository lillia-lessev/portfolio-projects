"""
Unit tests
"""

from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch
from django.utils import timezone
from django.urls import reverse
from news.models import CustomUser, Article, Publisher, Newsletter


class ArticleAPITestCase(TestCase):
    """Test cases for Article API endpoints"""
    
    def setUp(self):
        """Create test users, publisher and article"""
        self.client = APIClient()
        self.web_client = Client()
        
        self.reader = CustomUser.objects.create_user(
            username='reader1', 
            email='reader1@test.com',
            password='password1',
            role='reader'
        )
        
        self.journalist = CustomUser.objects.create_user(
            username='journalist1', 
            email='journalist1@test.com',
            password='password1',
            role='journalist'
        )
        
        self.other_journalist = CustomUser.objects.create_user(
            username='journalist2', 
            email='journalist2@test.com',
            password='password2',
            role='journalist'
        )
        
        self.editor = CustomUser.objects.create_user(
            username='editor1', 
            email='editor1@test.com',
            password='password1',
            role='editor'
        )
        
        self.publisher_user = CustomUser.objects.create_user(
            username='publisher1', 
            email='publisher1@test.com',
            password='password1',
            role='publisher'
        )
        
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            owner=self.publisher_user
        )
        
        # Creating approved article
        self.article = Article.objects.create(
            title='Approved Article',
            content='Some content',
            author=self.journalist,
            publisher=self.publisher,
            approved=True,
            approved_at=timezone.now()
        )
        
        self.reader.subscribed_publishers.add(self.publisher)
    
        self.publisher.journalists.add(self.journalist)
    
        # Newsletters
        self.subscribed_newsletter = Newsletter.objects.create(
            title="Subscribed Newsletter",
            description='From a journalist the reader follows',
            author=self.journalist,
        )
        
        self.unsubscribed_newsletter = Newsletter.objects.create(
            title="Unsubscribed Newsletter",
            description='From a journalist the reader does NOT follow',
            author=self.other_journalist,
        )
    # ----------- Authenticated access per role ----------------
    # API
    
    def test_reader_can_list_approved_articles(self):
        token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        
    def test_journalist_can_list_approved_articles(self):
        token = Token.objects.create(user=self.journalist)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)

    def test_editor_can_list_approved_articles(self):
        token = Token.objects.create(user=self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        
    def test_publisher_can_list_approved_articles(self):
        token = Token.objects.create(user=self.publisher_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
            
    def test_journalist_can_create_article(self):
        """Journalist should be able to create new article"""
        token=Token.objects.create(user=self.journalist)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = {'title': 'New Article', 'content': 'Body Text'}
        response = self.client.post('/api/articles/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertFalse(Article.objects.get(title='New Article').approved)
        
        self.assertEqual(response.status_code, 201)
        self.assertFalse(Article.objects.get(title='New Article').approved)
        
    def test_reader_cannot_create_article(self):
        """Reader shouldn't be able to create article"""
        token=Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = {'title': 'Unauthorized', 'content': 'Should fail'}
        response = self.client.post('/api/articles/', data, format='json')
        
        self.assertEqual(response.status_code, 403)
        
    def test_editor_cannot_create_article(self):
        """Editor shouldn't be able to create article (only edit)"""
        token=Token.objects.create(user=self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = {'title': 'Editor Article', 'content': 'Should fail'}
        response = self.client.post('/api/articles/', data, format='json')
        
        self.assertEqual(response.status_code, 403)
    
    # Test reader can only access subscribed newsletters
        def test_reader_access_subscribed_endpoint(self):
            """Test reader can only see newsletters from those they've subscribed to"""
            Article.objects.create(
                title='Unsubscribed Article', content='Should not appear',
                author=self.other_journalist, approved=True, approved_at=timezone.now()
            )    
            
            token = Token.objects.create(user=self.reader)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
            response = self.client.get('/api/articles/subscribed/')
            self.assertEqual(response.status_code, 200)
            titles = [item['title'] for item in response.data]
            self.assertIn('Approved Article', titles)
            self.assertNotIn('Unsubscribed Article', titles)
        
        def test_non_reader_cannot_access_subscribed_endpoint(self):
            """Test non-reader cannot access subscribed endpoint"""
            token = Token.objects.create(user=self.journalist)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
            response = self.client.get('/api/articles/subscribed/')
            self.assertEqual(response.status_code, 403)
    
    
    
    # Test editor can delete articles
    def test_editor_can_delete_article(self):
        token=Token.objects.create(user=self.editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = self.client.delete(f'/api/articles/{self.article.pk}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())
        
    def test_journalist_can_delete_own_article(self):
        token=Token.objects.create(user=self.journalist)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = self.client.delete(f'/api/articles/{self.article.pk}/')
        
        self.assertEqual(response.status_code, 204)
        
    def test_reader_cannot_delete_article(self):
        token=Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = self.client.delete(f'/api/articles/{self.article.pk}/')
        
        self.assertEqual(response.status_code, 403)

    # --------------- Testing newsletters -----------------------
    def test_newsletter_created_by_journalist(self):
        newsletter = Newsletter.objects.create(
            title='Newsletter Title',
            description='A test newsletter',
            author=self.journalist,
        )
        
        newsletter.articles.add(self.article)
        
        self.assertEqual(newsletter.articles.count(), 1)
        self.assertEqual(str(newsletter), 'Newsletter Title')
        
    def test_newsletter_belongs_to_journalist(self):
        newsletter = Newsletter.objects.create(
            title='Newsletter Title',
            description='A test newsletter',
            author=self.journalist,
        )
        
        newsletter.articles.add(self.article)
        
        self.assertEqual(newsletter.author.role, 'journalist')
        self.assertIn(newsletter, self.journalist.newsletters.all())
        
    # Newsletter filtering by role
    def test_reader_sees_subscribed_newsletters(self):
        """Reader can only see newsletters by those they've subscribed to"""
        self.web_client.login(username='reader1', password='password1')
        response = self.web_client.get(reverse('newsletter-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Subscribed Newsletter', content)
        
    def test_unsubscribed_reader_no_newsletters(self):
        """Reader can't see newsletters from those they haven't subscribed to"""
        reader2 = CustomUser.objects.create_user(
            username='reader2', 
            email='reader2@test.com',
            password='password1',
            role='reader'
        )
        self.web_client.login(username='reader2', password='password1')
        response = self.web_client.get(reverse('newsletter-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn('Subscribed Newsletter', content)
        self.assertNotIn('Unsubscribed Newsletter', content)
    
    def test_journalist_sees_all_newsletters(self):
        self.web_client.login(username='journalist1', password='password1')
        response = self.web_client.get(reverse('newsletter-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Subscribed Newsletter', content)
        self.assertIn('Unsubscribed Newsletter', content)

    def test_editor_sees_all_newsletters(self):
        self.web_client.login(username='editor1', password='password1')
        response = self.web_client.get(reverse('newsletter-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Subscribed Newsletter', content)
        self.assertIn('Unsubscribed Newsletter', content)
        
    def test_publisher_sees_all_newsletters(self):
        self.web_client.login(username='publisher1', password='password1')
        response = self.web_client.get(reverse('newsletter-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Subscribed Newsletter', content)
        self.assertIn('Unsubscribed Newsletter', content)
    
    @patch('news.signals.requests.post') # patch temporarily replaces real function with a fake one during test
    @patch('news.signals.send_mail')
    def test_approval_triggers_email_and_post(self, mock_mail, mock_post):
        """Approving an article should send email and POST to /api/approved/"""
        
        # Making sure reader is subscribed
        self.reader.subscribed_journalists.add(self.journalist)
        
        article = Article.objects.create(
            title="Pending Article",
            content='Awaiting approval',
            author=self.journalist,
            approved=False            
        )
        
        article.approved=True
        article.save()
        
        mock_mail.assert_called()
        mock_post.assert_called()
    