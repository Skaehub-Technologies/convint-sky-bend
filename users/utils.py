from typing import Any

from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(data: Any) -> None:
        print(data)
        email = EmailMessage(
            subject=data.get("subject"),
            body=data.get("body"),
            to=[data.get("recipient")],
        )
        email.send()
