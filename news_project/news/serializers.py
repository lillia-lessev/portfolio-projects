"""
Django REST framework serializers for News Application
"""

from rest_framework import serializers
from .models import Article, Newsletter, Publisher, CustomUser


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for publisher model"""

    class Meta:
        """Meta"""
        model = Publisher
        fields = ['id', 'name', 'description']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""

    author = serializers.StringRelatedField(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        """Meta"""
        model = Article
        fields = ['id', 'title', 'content', 'author',
                  'publisher', 'created_at', 'approved']
        read_only_fields = ['approved', 'author']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model"""

    class Meta:
        """Meta"""
        model = Newsletter
        fields = ['id', 'title', 'description', 'author', 'articles']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""

    class Meta:
        """Meta"""
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']
