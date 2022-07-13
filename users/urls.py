from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PasswordResetAPIView,
    PasswordResetEmailView,
    ProfileView,
    UserFollowView,
    UserTokenObtainPairView,
)

urlpatterns = [
    path(
        "auth/login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("auth/profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path(
        "auth/reset-password-request/",
        PasswordResetEmailView.as_view(),
        name="reset-password-request",
    ),
    path(
        "auth/reset-password-verify/<uidb64>/<token>",
        PasswordResetAPIView.as_view(),
        name="reset-password",
    ),
    path(
        "users/follow/<int:pk>/", UserFollowView.as_view(), name="user-follow"
    ),
]
