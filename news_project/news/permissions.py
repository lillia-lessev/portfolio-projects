"""
Custom permission classes for role-based access control
"""
from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """Only journalists have access"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'journalist'
        )


class IsEditor(BasePermission):
    """Only editors have access"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'editor'
        )


class IsEditorOrJournalist(BasePermission):
    """Only editors or journalists have access"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('editor', 'journalist')
        )
