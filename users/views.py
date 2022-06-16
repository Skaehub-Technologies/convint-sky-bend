from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserTokenObtainPairSerializer


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer
