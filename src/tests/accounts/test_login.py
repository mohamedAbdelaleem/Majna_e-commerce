from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status


class LoginTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email="test@test.com", password="12345aa", email_confirmed=True
        )
        cls.login_url = reverse("auth:login")
        customer_group = Group.objects.create(name="Customer")
        cls.user.groups.add(customer_group)
        cls.user.save()

    def test_success_login(self):
        valid_data = {"email": self.user.email, "password": "12345aa"}

        response = self.client.post(self.login_url, data=valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertEqual(response.data["user"]["user_role"], "Customer")

    def test_invalid_credentials_failure(self):
        invalid_data = {"email": "test12@test.com", "password": "12345aa"}

        response = self.client.post(self.login_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNotIn("token", response.data)

    def test_missing_credentials_failure(self):
        missing_data = {
            "email": self.user.email,
        }

        response = self.client.post(self.login_url, data=missing_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_insensitive_email_address_success(self):
        uppercase_email_data = {"email": self.user.email.upper(), "password": "12345aa"}

        email_containing_dots = {"email": "te.st@test.com", "password": "12345aa"}

        response = self.client.post(self.login_url, data=uppercase_email_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

        response = self.client.post(self.login_url, data=email_containing_dots)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_unconfirmed_email_failure(self):

        user = get_user_model().objects.create_user(
            email="test2@test.com", password="123"
        )

        data = {"email": user.email, "password": "123"}

        response = self.client.post(self.login_url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn("token", response.data)
