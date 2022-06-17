from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView

from .serializers import UserTokenObtainPairSerializer
from .models import Profile
from .serializers import ProfileSerializer

class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer

class ProfileView(ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    