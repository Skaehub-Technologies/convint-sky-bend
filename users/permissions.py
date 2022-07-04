from typing import Any

from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: Any, view: Any) -> Any:
        # Authenticated users only can see list view
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        # allow GET, HEAD, or OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
            # Write permissions are only allowed to the account owner
        return obj.user == request.user
