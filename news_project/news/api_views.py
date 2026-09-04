"""
API views for News Application
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import Article
from .serializers import ArticleSerializer
from .permissions import IsJournalist, IsEditorOrJournalist


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing, creating, updating & deleting Articles."""

    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Return permissions depending on action"""

        if self.action == 'create':
            return [IsJournalist()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsEditorOrJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Automatically set author to current user +
        mark article as not approved
        """

        serializer.save(author=self.request.user, approved=False)

    @action(detail=False, methods=['get'], url_path='subscribed')
    def subscribed(self, request):
        """
        Return articles from publishers / journalists
        that current reader is subscribed to
        """
        user = request.user

        if user.role != 'reader':
            return Response(
                {'detail': 'Only readers can access subscribed content.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get articles from database which have been approved
        queryset = Article.objects.filter(approved=True).filter(
            # Gets publishers user's subscribed to OR
            Q(publisher__in=user.subscribed_publishers.all()) |
            # Gets journalists user's subscribed to
            Q(author__in=user.subscribed_journalists.all())
        ).distinct()  # Removes duplicates

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def approved_log(request):
    """
    Simple endpoint that receives approved article data.
    Used by signal to simulate external integration.
    """

    print("Approved article received:", request.data)
    return Response({'status': 'logged'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    """
    Obtain authentication token using username + password
    """

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        # token object, created boolean
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_400_BAD_REQUEST
    )
