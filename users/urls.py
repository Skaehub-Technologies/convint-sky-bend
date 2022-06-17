from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserTokenObtainPairView
from .views import ProfileView

urlpatterns = [
    path(
        "login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]


