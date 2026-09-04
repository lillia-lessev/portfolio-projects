"""
URL configuration
"""
from django.urls import path, include, reverse_lazy
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    )
from . import api_views, views

router = DefaultRouter()
router.register(r'articles', api_views.ArticleViewSet, basename='api-article')

urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    path('articles/', views.article_list,
         name='article-list'),
    path('articles/<int:pk>/', views.article_detail,
         name='article-detail'),
    path('articles/create/', views.article_create,
         name='article-create'),
    path('articles/<int:pk>/edit', views.article_edit,
         name='article-edit'),
    path('articles/<int:pk>/delete', views.article_delete,
         name='article-delete'),
    path('articles/approve/', views.article_approve_list,
         name='article-approve-list'),
    path('articles/<int:pk>/approve/', views.article_approve,
         name='article-approve'),
    path('newsletters/', views.newsletter_list,
         name='newsletter-list'),
    path('newsletter/<int:pk>/', views.newsletter_detail,
         name='newsletter-detail'),
    path('newsletter/create/', views.newsletter_create,
         name='newsletter-create'),
    path('newsletter/<int:pk>/edit', views.newsletter_edit,
         name='newsletter-edit'),
    path('newsletter/<int:pk>/delete', views.newsletter_delete,
         name='newsletter-delete'),

    # Journalists and publishers
    path('journalists-publishers/', views.journalist_publisher_list,
         name='journalist-publisher-list'),
    path('subscribe/publisher/<int:pk>/', views.subscribe_publisher,
         name='subscribe-publisher'),
    path('subscribe/journalist/<int:pk>/', views.subscribe_journalist,
         name='subscribe-journalist'),
    path('unsubscribe/publisher/<int:pk>/', views.unsubscribe_publisher,
         name='unsubscribe-publisher'),
    path('unsubscribe/journalist/<int:pk>/', views.unsubscribe_journalist,
         name='unsubscribe-journalist'),
    path('publisher/<int:pk>/articles/', views.publisher_articles,
         name='publisher-articles'),
    path('journalist/<int:pk>/articles/', views.journalist_articles,
         name='journalist-articles'),

    # Authentication
    path('login/', views.LoginView.as_view(template_name='news/login.html'),
         name='login'),
    path('logout/', views.LogoutView.as_view(next_page='home'),
         name='logout'),
    path('register', views.register,
         name='register'),

    # Password reset
    path(
        'password-reset',
        PasswordResetView.as_view(
            template_name='news/password_reset_form.html',
            email_template_name='news/password_reset_email.html',
            subject_template_name='news/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset-done',
        PasswordResetDoneView.as_view(
            template_name='news/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='news/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        PasswordResetCompleteView.as_view(
            template_name='news/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),


    # API
    path('api/', include(router.urls)),
    path('api/approved/', api_views.approved_log, name='approved-log'),
    path('api/token/', api_views.obtain_token, name='api-token'),
]
