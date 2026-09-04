"""apps.py"""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for nes application"""

    default_auto_filed = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """Import signal when app is ready"""
        import news.signals
