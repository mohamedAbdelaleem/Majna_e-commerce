from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

from .managers import CustomerManager, CustomUserManager, DistributorManager
from .utils import clean_email


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    phone_num = models.CharField(max_length=15, null=True)
    email_confirmed = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    @property
    def is_customer(self) -> bool:
        return self.groups.filter(name="Customer").exists()

    @property
    def is_distributor(self) -> bool:
        return self.groups.filter(name="Distributor").exists()

    @property
    def is_reviewer(self) -> bool:
        return self.groups.filter(name="Reviewer").exists()

    @property
    def is_delivery(self) -> bool:
        return self.groups.filter(name="Delivery").exists()

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_password_reset_email(self):
        subject = "Password Reset"
        token = default_token_generator.make_token(user=self)
        password_reset_link = (
            settings.FRONTEND_BASE_URL + f"reset-password/{self.pk}/{token}"
        )
        html_message = render_to_string(
            "password_reset.html", {"password_reset_link": password_reset_link}
        )
        text_message = strip_tags(html_message)
        self.email_user(subject, text_message, html_message=html_message)

    def activate_email(self):
        self.email_confirmed = True
        self.save()

    def clean(self):
        super().clean()
        self.email = clean_email(self.email)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT)

    objects = CustomerManager()

    def save(self, *args, **kwargs):
        self.id = self.user_id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.get_username()


class Distributor(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT)

    objects = DistributorManager()

    def save(self, *args, **kwargs):
        self.id = self.user_id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.get_username()
