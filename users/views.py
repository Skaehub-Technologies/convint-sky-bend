from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserTokenObtainPairSerializer
from .models import Profile
from .serializers import ProfileSerializer

class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer

class ProfileView(RetrieveUpdateDestroyAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def post(self, request):
        current_user = request.user
        data = request.data
        profile = Profile.objects.filter(user=current_user.pk)
        if profile:
            serializer = ProfileSerializer(profile, many=True)
            return Response(serializer.data)
        else:
            serializer = ProfileSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=current_user)
                new_data = serializer.data
                return Response(new_data)
            return Response(serializer.errors)
    