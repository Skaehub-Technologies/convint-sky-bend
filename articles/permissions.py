from typing import Any

from rest_framework import permissions


class IsAuthorEditorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Any, view: Any) -> Any:
        """cannot view article but cannot edit or delete"""
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        """can only edit and delete own article"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_superuser
            or request.user.is_editor
        )
