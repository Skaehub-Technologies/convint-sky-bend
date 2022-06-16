from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterUser, UserTokenObtainPairView

from .views import UserTokenObtainPairView

urlpatterns = [
    path(
        "login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", RegisterUser.as_view(), name="register"),
]
