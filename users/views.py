from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserTokenObtainPairSerializer


from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from .models import Profile
User = get_user_model()
# class RegisterUser(generics.GenericAPIView):
#     serializer_class = UserSerializer
#     permission_classes = (permissions.AllowAny,)
    
#     def post(self, request, *args,  **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user,    context=self.get_serializer_context()).data,
#             "message": "User registered Successfully.  Proceed to Login to get your token",
#         })

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    #permission_classes = (permissions.IsAuthenticated,)

class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer
