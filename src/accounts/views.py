from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from common.api.exceptions import Conflict
from majna.tasks import send_confirmation_email
from . import serializers as local_serializer


class UsersView(APIView):
    def post(self, request: Request) -> Response:
        user = local_serializer.UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user = user.save()

        if settings.REQUIRE_ACCOUNT_ACTIVATION:
            send_confirmation_email.delay(user.pk)

        return Response(status=status.HTTP_201_CREATED)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        if kwargs["pk"] != request.user.pk:
            raise PermissionDenied("UnAuthorized user")

        serializer = local_serializer.PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data={"message": "Password changed successfully"})


class EmailConfirmationView(APIView):
    def post(self, request, **kwargs):
        pk = kwargs.get("pk")
        serializer = local_serializer.EmailTokenSerializer(
            data=request.data, context={"pk": pk}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if user.email_confirmed:
            raise Conflict()

        user.email_confirmed = True
        user.save()

        return Response(data={"message": "Email Confirmed Successfully!"})


class ResendEmailConfirmationView(APIView):
    def post(self, request):
        serializer = local_serializer.SendEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if not user.email_confirmed and settings.REQUIRE_ACCOUNT_ACTIVATION:
                user.send_email_confirmation_email()

        return Response(
            data={"message": "An Email has been Sent if this is a valid email"}
        )


class PasswordResetEmailView(APIView):
    def post(self, request):
        serializer = local_serializer.SendEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.send_password_reset_email()
            return Response(
                data={"message": "An Email has been Sent if this is a valid email"}
            )

        return Response(
            data={"message": "Email not found!"}, status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetView(APIView):
    def post(self, request, **kwargs):

        serializer = local_serializer.EmailTokenSerializer(
            data=request.data, context={"pk": kwargs["pk"]}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if not user.email_confirmed:
            user.activate_email()
        if "password" not in request.data:
            return Response(
                data={"message": "Password Required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {"password": request.data["password"]}
        user_serializer = local_serializer.UserSerializer(user, data=data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        return Response(data={"message": "Password reset Successfully"})
