from typing import Any

from rest_framework import permissions


class CanRegisterbutcantGetList(permissions.BasePermission):
    """cannot view list of users but can register new account"""

    def has_permission(self, request: Any, view: Any) -> Any:
        return request.method == "POST"

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser
