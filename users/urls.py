from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserFollow, UserTokenObtainPairView

urlpatterns = [
    path(
        "auth/login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("users/follow/<int:pk>/", UserFollow.as_view(), name="user-follow"),
]
