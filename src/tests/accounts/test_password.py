from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from knox.models import AuthToken


class ChangePasswordTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123"
        )
        cls.url = reverse("accounts:change_password", kwargs={"pk": cls.user.pk})
        instance, cls.token = AuthToken.objects.create(user=cls.user)

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_success_change_password(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertTrue(check_new_password)

        # check hashing
        self.assertFalse(self.user.password == data["new_password"])

    def test_wrong_current_password_failure(self):
        data = {
            "current_password": "1234",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_passwords_mismatch_failure(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "1212aa",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_invalid_password_failure(self):
        data = {
            "current_password": "123",
            "new_password": "123123",
            "re_new_password": "123123",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.user.refresh_from_db()
        check_new_password = self.user.check_password(data["new_password"])
        self.assertFalse(check_new_password)

    def test_unauthenticated_user(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        self.client.credentials()

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_same_user_failure(self):
        data = {
            "current_password": "123",
            "new_password": "123123aa",
            "re_new_password": "123123aa",
        }

        url = reverse("accounts:change_password", kwargs={"pk": self.user.pk + 1})
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PasswordResetEmailTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123"
        )
        cls.url = reverse("accounts:password_reset_request")

    def test_password_reset_request(self):
        data = {"email": self.user.email}

        response = self.client.post(path=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_invalid_email_failure(self):
        data = {"email": "test22@test.com"}
        response = self.client.post(path=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)


class PasswordResetTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="123"
        )
        cls.token = default_token_generator.make_token(user=cls.user)
        cls.url = reverse("accounts:reset_password", kwargs={"pk": cls.user.pk})

    def test_success_password_reset(self):
        data = {"token": self.token, "password": "12345aa"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data["password"]))

    def test_invalid_token_failure(self):
        data = {"token": self.token + "dsaf", "password": "12345aa"}
        response = self.client.post(self.url, data=data)
        is_failed = self.is_failed(response)
        self.assertTrue(is_failed)

    def test_invalid_pk_failure(self):
        data = {"token": self.token, "password": "12345aa"}
        url = reverse("accounts:reset_password", kwargs={"pk": self.user.pk + 2})
        response = self.client.post(url, data=data)
        is_failed = self.is_failed(response)
        self.assertTrue(is_failed)

    def test_invalid_password_failure(self):
        data = {"token": self.token + "dsaf", "password": "12345aa"}
        response = self.client.post(self.url, data=data)
        is_failed = self.is_failed(response)
        self.assertTrue(is_failed)

    def is_failed(self, response):
        failed = True

        if response.status_code != 400:
            failed = False
        old_password = self.user.password
        self.user.refresh_from_db()
        if old_password != self.user.password:
            failed = False

        return failed

    def test_confirm_email(self):
        """
        Test User's email address confirmation in case of a valid token
        and unconfirmed email address
        """
        data = {"token": self.token, "password": "1234"}
        self.client.post(self.url, data=data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_confirmed)
