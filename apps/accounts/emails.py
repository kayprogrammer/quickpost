from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils import timezone
import random, threading


# We're using threading for now, but a better option is celery and we'll update it later
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    async def send_otp(user, purpose):
        code = random.randint(100000, 999999)
        message = render_to_string(
            "email-otp.html",
            {
                "name": user.full_name,
                "otp": code,
                "purpose": purpose,
                "expiry_minutes": 15,
            },
        )
        user.otp_code = code
        user.otp_expires_at = timezone.now()
        await user.asave()
        email_message = EmailMessage(
            subject=purpose.title(), body=message, to=[user.email]
        )
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def password_reset_confirmation(user):
        message = render_to_string(
            "password-reset-success.html",
            {
                "name": user.full_name,
            },
        )
        email_message = EmailMessage(
            subject="Password Reset Successful!", body=message, to=[user.email]
        )
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def welcome_email(user):
        message = render_to_string(
            "welcome.html",
            {
                "name": user.full_name,
            },
        )
        email_message = EmailMessage(
            subject="Account verified!", body=message, to=[user.email]
        )
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
