from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.db.models import Q
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import CustomUser, Publisher, Article, Newsletter
from .forms import *


def home(request):
    """Homepage for root url"""
    return render(request, 'news/home.html')


def article_list(request):
    """Shows list of articles"""
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'news/article_list.html', {'articles': articles})


def article_detail(request, pk):
    """Shows article"""
    article = get_object_or_404(Article, pk=pk)

    if not article.approved:
        user = request.user
        is_editor = user.is_authenticated and user.role == 'editor'
        is_author = user.is_authenticated and article.author == user
        if not (is_editor or is_author):
            messages.error(request, 'This article is not approved yet.')
            return redirect('article-list')

    return render(request, 'news/article_detail.html', {'article': article})


def newsletter_detail(request, pk):
    """Shows newsletter"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    articles = newsletter.articles.filter(
        approved=True
    ).order_by('-created_at')
    return render(request, 'news/newsletter_detail.html', {
        'newsletter': newsletter,
        'articles': articles,
    })


@login_required
def article_create(request):
    """Create article"""
    if request.user.role != 'journalist':
        messages.error(request,
                       'Only logged-in journalists can write articles.')
        return redirect('home')

    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            messages.success(request, 'Article submitted for approval.')
            return redirect('article-list')
    else:
        form = ArticleForm()

    return render(request, 'news/article_form.html', {'form': form})


@login_required
def article_edit(request, pk):
    """Edit article"""
    article = get_object_or_404(Article, pk=pk)
    is_journalist = request.user.groups.filter(name='Journalist').exists()
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (is_editor or (is_journalist and article.author == request.user)):
        messages.error(request,
                       'You do not have permission to edit this article.')
        return redirect('article-list')

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated.')
            return redirect('article-list')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'news/article_form.html', {'form': form})


@login_required
def article_delete(request, pk):
    """Delete article"""
    article = get_object_or_404(Article, pk=pk)
    is_journalist = request.user.groups.filter(name='Journalist').exists()
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (is_editor or (is_journalist and article.author == request.user)):
        messages.error(request,
                       'You do not have permission to delete this article.')
        return redirect('article-list')

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted.')
        return redirect('article-list')

    return render(request,
                  'news/article_confirm_delete.html', {'article': article})


@login_required
def newsletter_create(request):
    """Create newsletter"""
    if not request.user.role == 'journalist':
        messages.error(request,
                       'Only logged-in journalists can create newsletters.')
        return redirect('newsletter-list')

    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()
            messages.success(request, 'Newsletter created.')
            return redirect('newsletter-list')
    else:
        form = NewsletterForm()

    return render(request, 'news/newsletter_form.html', {'form': form})


@login_required
def newsletter_edit(request, pk):
    """Edit newsletter"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    is_journalist = request.user.groups.filter(name='Journalist').exists()
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (is_editor or (is_journalist and newsletter.author == request.user)):
        messages.error(request,
                       'You do not have permission to edit this newsletter.')
        return redirect('newsletter-list')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated.')
            return redirect('newsletter-list')
    else:
        form = NewsletterForm(instance=newsletter)

    return render(request, 'news/newsletter_form.html', {'form': form})


@login_required
def newsletter_delete(request, pk):
    """Delete Newsletter"""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    is_journalist = request.user.groups.filter(name='Journalist').exists()
    is_editor = request.user.groups.filter(name='Editor').exists()

    if not (is_editor or (is_journalist and newsletter.author == request.user)):
        messages.error(request,
                       'You do not have permission to delete this newsletter.')
        return redirect('newsletter-list')

    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted.')
        return redirect('newsletter-list')

    return render(request,
                  'news/newsletter_confirm_delete.html',
                  {'newsletter': newsletter})


@login_required
def article_approve_list(request):
    """List of articles waiting for approval"""
    if request.user.role != 'editor':
        messages.error(request, 'Only editors can approve articles.')
        return redirect('home')

    articles = Article.objects.filter(approved=False).order_by('-created_at')
    return render(request,
                  'news/article_approve_list.html',
                  {'articles': articles})


@login_required
def article_approve(request, pk):
    """Approve articles"""
    if request.user.role != 'editor':
        messages.error(request, 'Only editors can approve articles.')
        return redirect('home')

    article = get_object_or_404(Article, pk=pk, approved=False)
    article.approved = True
    article.approved_at = timezone.now()
    article.save()
    messages.success(request, f'"{ article.title }" by { article.author } has been approved.')
    return redirect('article-approve-list')


def newsletter_list(request):
    """
    Publishers, journalists, editors can see all newsletters.
    Readers can only see newsletters from those they have subscribed to.
    """
    if request.user.is_authenticated and request.user.role == 'reader':
        # Newsletters from subscribed journalists
        newsletters = Newsletter.objects.filter(
            Q(author__in=request.user.subscribed_journalists.all()) |
            Q(author__publisher_journalists__in=request.user.subscribed_publishers.all())
            ).distinct().order_by('-created_at')
    elif request.user.is_authenticated:
        # Show all newsletters to other logged-in users
        newsletters = Newsletter.objects.all().order_by('-created_at')
    else:
        newsletters = Newsletter.objects.none()

    return render(request,
                  'news/newsletter_list.html',
                  {'newsletters': newsletters})


def journalist_publisher_list(request):
    """Show all publishers and journalists"""
    publishers = Publisher.objects.prefetch_related('journalists',
                                                    'editors').all()
    independent_journalists = CustomUser.objects.filter(
        role='journalist'
    ).exclude(
        publisher_journalists__isnull=False
    ).distinct()

    return render(request, 'news/journalist_publisher_list.html', {
        'publishers': publishers,
        'independent_journalists': independent_journalists
    })


@login_required
def subscribe_publisher(request, pk):
    """Subscribe to publisher"""
    if request.user.role != 'reader':
        messages.error(request, 'Only readers can subscribe.')
        return redirect('journalist-publisher-list')
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscribed_publishers.add(publisher)
    messages.success(request, f"You subscribed to {publisher.name}.")
    return redirect('journalist-publisher-list')


@login_required
def unsubscribe_publisher(request, pk):
    """Unsubscribe from publisher"""
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscribed_publishers.remove(publisher)
    messages.success(request, f"You unsubscribed from {publisher.name}.")
    return redirect('journalist-publisher-list')


@login_required
def subscribe_journalist(request, pk):
    """Subscribe to journalist"""
    if request.user.role != 'reader':
        messages.error(request, 'Only readers can subscribe.')
        return redirect('journalist-publisher-list')
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')
    request.user.subscribed_journalists.add(journalist)
    messages.success(request, f"You subscribed to {journalist.username}.")
    return redirect('journalist-publisher-list')


@login_required
def unsubscribe_journalist(request, pk):
    """Unsubscribe from journalist"""
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')
    request.user.subscribed_journalists.remove(journalist)
    messages.success(request, f"You unsubscribed from {journalist.username}.")
    return redirect('journalist-publisher-list')


def publisher_articles(request, pk):
    """Articles part of certain publisher"""
    publisher = get_object_or_404(Publisher, pk=pk)
    articles = Article.objects.filter(publisher=publisher,
                                      approved=True).order_by('-created_at')
    return render(request, 'news/filtered_articles.html', {
        'title': f'Articles from {publisher.name}',
        'articles': articles,
    })


def journalist_articles(request, pk):
    """Articles by certain journalist"""
    journalist = get_object_or_404(CustomUser, pk=pk, role='journalist')
    articles = Article.objects.filter(author=journalist,
                                      approved=True).order_by('-created_at')
    return render(request, 'news/filtered_articles.html', {
        'title': f'Articles by {journalist.username}',
        'articles': articles,
    })


# ---------- Registration ---------------
class RegisterForm(UserCreationForm):
    """Registration form"""
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label='Confirm Password')

    role = forms.ChoiceField(
        choices=[
            ('reader', 'Reader'),
            ('journalist', 'Journalist'),
            ('editor', 'Editor'),
            ('publisher', 'Publisher'),
        ]
    )
    email = forms.EmailField(required=True)

    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        empty_label='- Independent / None -',
        help_text=('Optional. Journalists / Editors can choose'
                   + ' to be part of a publisher or be independent.')
    )

    class Meta:
        """Meta"""
        model = CustomUser
        fields = ['username', 'email', 'role']

    def clean_email(self):
        """clean_email"""
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            # iexact makes it ignore case (case insensitivity)
            raise forms.ValidationError('An account with this'
                                        + ' email address already exists.')
        return email

    def clean_role(self):
        """clean_role"""
        role = self.cleaned_data['role']
        if role not in ('reader', 'journalist', 'editor', 'publisher'):
            raise forms.ValidationError('Invalid Role.')
        return role

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        role = cleaned.get('role')
        publisher = cleaned.get('publisher')
        if publisher and role not in ('journalist', 'editor'):
            raise forms.ValidationError('Only journalists and editors can'
                                        + ' be part of a publishing house.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            publisher = self.cleaned_data.get('publisher')
            if publisher and user.role == 'journalist':
                publisher.journalists.add(user)
            elif publisher and user.role == 'editor':
                publisher.editors.add(user)
            elif user.role == 'publisher':
                # Create publishing house
                Publisher.objects.create(
                    name=user.username,
                    owner=user
                )
        return user


def register(request):
    """Register"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Congratulations, {user.username}! You have successfully created your {user.role} account.'
            )
            if form.cleaned_data.get('publisher'):
                messages.info(
                    request,
                    f'You joined the publisher: {form.cleaned_data["publisher"].name}.'
                )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'news/register.html', {'form': form})
