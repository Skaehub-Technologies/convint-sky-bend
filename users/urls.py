from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from .views import UserTokenObtainPairView, UserDetail,UserList

urlpatterns = [
    path(
        "login/",
        UserTokenObtainPairView.as_view(),
        name="login",
    ),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("register/", UserList.as_view(), name="register"),
    path("users/", UserList.as_view(), name="users"),
    path("user/<int:pk>/", UserDetail.as_view(), name="user-detail"),
    path("user/<int:pk>/update/", UserDetail.as_view(), name="user-update"),
    path("user/<int:pk>/delete/", UserDetail.as_view(), name="user-delete"),   
    
]
