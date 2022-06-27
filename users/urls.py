from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PasswordResetAPIView,
    PasswordResetEmail,
    UserTokenObtainPairView,
)

urlpatterns = [
    path(
        "auth/login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path(
        "auth/reset-password-request/",
        PasswordResetEmail.as_view(),
        name="reset-password-request",
    ),
    path(
        "auth/reset-password-verify/<uidb64>/<token>",
        PasswordResetAPIView.as_view(),
        name="reset-password-verify",
    ),
    path(
        "auth/reset-password/",
        PasswordResetAPIView.as_view(),
        name="reset-password",
    ),
]
