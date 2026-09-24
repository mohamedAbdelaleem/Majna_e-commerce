from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()


@shared_task()
def send_confirmation_email(user_pk: int):
    user = User.objects.get(id=user_pk)
    subject = "Email Confirmation"
    token = default_token_generator.make_token(user=user)
    confirmation_link = (
        settings.FRONTEND_BASE_URL + f"activate-account/{user.pk}/{token}"
    )
    html_message = render_to_string(
        "email_confirmation.html", {"confirmation_link": confirmation_link}
    )
    text_message = strip_tags(html_message)
    user.email_user(subject, text_message, html_message=html_message)
