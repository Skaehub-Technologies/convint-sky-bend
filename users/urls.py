from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PasswordResetAPIView,
    PasswordResetEmailView,
    ProfileView,
    UserDetail,
    UserFollowView,
    UserList,
    UserTokenObtainPairView,
    VerifyEmail,
)

urlpatterns = [
    path(
        "auth/login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("profile/<str:lookup_id>/", ProfileView.as_view(), name="profile"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("users/", UserList.as_view(), name="users"),
    path("user/<str:lookup_id>/", UserDetail.as_view(), name="user-detail"),
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
        "auth/verify-email/<str:uidb64>/<str:token>/",
        VerifyEmail.as_view(),
        name="verify-email",
    ),
    path(
        "users/follow/<str:lookup_id>/",
        UserFollowView.as_view(),
        name="user-follow",
    ),
]
