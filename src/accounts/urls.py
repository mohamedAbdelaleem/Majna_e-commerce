from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.UsersView.as_view(), name="users"),
    path(
        "resend-confirmation-email",
        views.ResendEmailConfirmationView.as_view(),
        name="resend_confirmation",
    ),
    path(
        "password-reset-request",
        views.PasswordResetEmailView.as_view(),
        name="reset_password_email",
    ),
    path(
        "<int:pk>/password-reset",
        views.PasswordResetView.as_view(),
        name="reset_password",
    ),
    path(
        "<int:pk>/password-change",
        views.PasswordChangeView.as_view(),
        name="change_password",
    ),
    path(
        "<int:pk>/email-confirm",
        views.EmailConfirmationView.as_view(),
        name="confirm_email",
    ),
]
