from typing import Any

from django.core.mail import send_mail
from django.template.loader import render_to_string

from core.settings import EMAIL_USER


class Util:
    @staticmethod
    def send_email(data: Any) -> None:
        email_body = render_to_string(
            "reset_password.html", {"body": data.get("body")}
        )
        send_mail(
            data.get("subject"),
            email_body,
            EMAIL_USER,
            [data.get("recipient")],
            fail_silently=False,
        )
