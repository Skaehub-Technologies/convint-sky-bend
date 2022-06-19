from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PasswordResetAPIView,
    PasswordResetEmail,
    UserTokenObtainPairView,
)

urlpatterns = [
    path(
        "login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path(
        "reset-password-request/",
        PasswordResetEmail.as_view(),
        name="reset-password-request",
    ),
    path(
        "reset-password/<uidb64>/<token>",
        PasswordResetAPIView.as_view(),
        name="reset-password-verify",
    ),
    path(
        "reset-password/",
        PasswordResetAPIView.as_view(),
        name="reset-password",
    ),
]
