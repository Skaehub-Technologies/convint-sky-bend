from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.request import Request

from core.settings import EMAIL_USER

User = get_user_model()


def generate_token(user: Any) -> Any:
    """
    Generates a user base64 encoded user id and token from the user instance passed
    """
    uidb64 = urlsafe_base64_encode(smart_bytes(user.lookup_id))
    token = PasswordResetTokenGenerator().make_token(user)
    return {"uidb64": uidb64, "token": token}


def create_email_data(
    request: Request, user: Any, token_data: str, url: str, subject: str
) -> dict:
    """
    Creates the email data to be sent to the user
    """
    relative_link = reverse(
        url,
        kwargs={
            "uidb64": token_data.get("uidb64"),  # type: ignore[attr-defined]
            "token": token_data.get("token"),  # type: ignore[attr-defined]
        },
    )
    current_site = get_current_site(request).domain
    absolute_url = f"http://{current_site}{relative_link}"
    body = {"user": user, "link": absolute_url}
    return {
        "subject": subject,
        "body": body,
        "recipient": user.email,
    }


def send_email(template: str, email_data: Any) -> None:
    """
    Sends the email to the user
    """
    email_body = render_to_string(template, {"body": email_data.get("body")})
    send_mail(
        email_data.get("subject"),
        email_body,
        EMAIL_USER,
        [email_data.get("recipient")],
        fail_silently=False,
    )


def verify_token(uidb64: Any, token: Any) -> Any:
    """
    Verifies the token and uidb64
    """
    try:
        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(lookup_id=uid)
        if PasswordResetTokenGenerator().check_token(user, token):
            return True
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return False
