from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PasswordResetAPIView,
    PasswordResetEmail,
    UserFollow,
    UserFollowingViewSet,
    UserTokenObtainPairView,
)

router = DefaultRouter()
router.register(
    r"userfollowing", UserFollowingViewSet, basename="userfollowing"
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
        "auth/reset-password/<uidb64>/<token>",
        PasswordResetAPIView.as_view(),
        name="reset-password-verify",
    ),
    path(
        "auth/reset-password/",
        PasswordResetAPIView.as_view(),
        name="reset-password",
    ),
    path("", include(router.urls)),
    path("users/follow/<int:pk>/", UserFollow.as_view(), name="user-follow"),
]
