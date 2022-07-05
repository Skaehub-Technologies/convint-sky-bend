from typing import Any

from rest_framework import permissions

"""'users can view list and detail of users but not delete, create or update unless they are superuser or its owner"""


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser
