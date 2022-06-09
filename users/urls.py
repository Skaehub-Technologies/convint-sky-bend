from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import UserTokenObtainPairView

urlpatterns = [
    path(
        "api/auth/login",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
]