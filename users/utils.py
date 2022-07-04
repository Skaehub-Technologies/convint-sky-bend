from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

from core.settings import EMAIL_USER

User = get_user_model()


class Util:
    @staticmethod
    def send_email(template: str, email_data: Any) -> None:
        email_body = render_to_string(
            template, {"body": email_data.get("body")}
        )
        send_mail(
            email_data.get("subject"),
            email_body,
            EMAIL_USER,
            [email_data.get("recipient")],
            fail_silently=False,
        )

    @staticmethod
    def generate_reset_token(email: str) -> Any:
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            return (user, uidb64, token)
        return None

    @staticmethod
    def create_reset_email(
        request: Any, user: Any, uidb64: str, token: str
    ) -> dict:
        current_site = get_current_site(request).domain
        relative_link = reverse(
            "reset-password",
            kwargs={"uidb64": uidb64, "token": token},
        )
        absurl = f"http://{current_site}{relative_link}"
        body = {"user": user, "link": absurl}
        data = {
            "subject": "PASSWORD RESET",
            "body": body,
            "recipient": user.email,
        }
        return data
