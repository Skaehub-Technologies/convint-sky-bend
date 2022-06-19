from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import generics  # , mixins, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, UserTokenObtainPairSerializer

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
    lookup_field = "pk"
    # permission_classes = (permissions.IsAuthenticated,)
    """allow only users to  delete own account"""

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        user = self.get_object()
        if user == request.user:
            self.perform_destroy(user)
            return Response({"message": "User deleted Successfully"})
        else:
            return Response(
                {"message": "You can only delete your own account"}
            )


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer
