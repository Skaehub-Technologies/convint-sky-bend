from typing import Any

from rest_framework import permissions


class CanRegisterbutcantGetList(permissions.BasePermission):
    def has_permission(self, request: Any, view: Any) -> Any:
        """cannot view list of users but can register new account"""
        # if not request.user.is_authenticated:
        # return request.method == "GET"
        # return request.method == "POST"
        if request.method == "POST":
            return True
        if request.user.is_authenticated:
            return True

        return False

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_superuser
