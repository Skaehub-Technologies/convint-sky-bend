from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    smart_bytes,
    smart_str,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    PasswordResetSerializer,
    PasswordSerializer,
    UserTokenObtainPairSerializer,
)
from .utils import Util

User = get_user_model()


class UserTokenObtainPairView(TokenObtainPairView):  # type: ignore
    serializer_class = UserTokenObtainPairSerializer


class PasswordResetEmail(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        data = {"email": request.data.get("email"), "request": request}

        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                email = request.data.get("email")
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                    token = PasswordResetTokenGenerator().make_token(user)

                    # create email
                    current_site = get_current_site(request).domain
                    relative_link = reverse(
                        "reset-password-verify",
                        kwargs={"uidb64": uidb64, "token": token},
                    )
                    absurl = f"http://{current_site}{relative_link}"
                    body = f"Hi {user.username} Use the link below to reset your password \n {absurl}"
                    data = {
                        "subject": "PASSWORD RESET",
                        "body": body,
                        "recipient": user.email,
                    }
                    Util.send_email(data)
            except KeyError:
                pass
            return Response(
                {"message": "check your email for password reset link"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "failed"}, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request: Any, uidb64: Any, token: Any) -> Any:
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid Token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response(
                {
                    "success": True,
                    "message": "valid cred",
                    "uidb64": uidb64,
                    "token": token,
                }
            )

        except DjangoUnicodeDecodeError:
            return Response(
                {"error": "Password reset failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def patch(self, request: Any) -> Any:
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"Password changed Successfully"}, status=status.HTTP_200_OK
        )
