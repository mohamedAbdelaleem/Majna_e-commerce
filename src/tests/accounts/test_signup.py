from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SignUpTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("accounts:users")
        user = get_user_model().objects.create_user(
            email="test@test.com", username="test", password="12345aa"
        )
        cls.user = user
        Group.objects.create(name="Customer")
        Group.objects.create(name="Distributor")

    def test_success_customer_signup(self):
        data = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "12345aa",
            "role": "customer",
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            user = get_user_model().objects.get(email=data["email"])
            # check encryption
            self.assertNotEqual(user.password, data["password"])

            # check if user is in the correct group
            self.assertTrue(user.is_customer)
            user_groups = user.groups.all()
            num_of_groups = user_groups.count()
            self.assertEqual(num_of_groups, 1)

            # check if email confirmation email was sent
            self.assertEqual(len(mail.outbox), 1)

        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist: the user wasn't created")

    def test_success_distributor_signup(self):
        data = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "12345aa",
            "role": "distributor",
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        try:
            user = get_user_model().objects.get(email=data["email"])
            # check encryption
            self.assertNotEqual(user.password, data["password"])
            # check if user is in the correct group
            self.assertTrue(user.is_distributor)
            user_groups = user.groups.all()
            num_of_groups = user_groups.count()
            self.assertEqual(num_of_groups, 1)
            # check if email confirmation email was sent
            self.assertEqual(len(mail.outbox), 1)

        except ObjectDoesNotExist:
            self.fail("ObjectDoesNotExist: the user wasn't created")

    def test_missing_credential_failure(self):
        missing_email = {
            "username": "testuser",
            "password": "12345aa",
            "role": "distributor",
        }

        missing_username = {
            "email": "test1@test.com",
            "password": "12345aa",
            "role": "distributor",
        }

        missing_password = {
            "email": "test1@test.com",
            "username": "testuser",
            "role": "customer",
        }
        missing_role = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "12345aa",
        }

        missing_email_response = self.client.post(self.url, missing_email)
        self.assertEqual(
            missing_email_response.status_code, status.HTTP_400_BAD_REQUEST
        )

        missing_username_response = self.client.post(self.url, missing_username)
        self.assertEqual(
            missing_username_response.status_code, status.HTTP_400_BAD_REQUEST
        )

        missing_password_response = self.client.post(self.url, missing_password)
        self.assertEqual(
            missing_password_response.status_code, status.HTTP_400_BAD_REQUEST
        )

        missing_role_response = self.client.post(self.url, data=missing_role)
        self.assertEqual(missing_role_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_email_failure(self):
        data = {
            "email": self.user.email,
            "username": "test",
            "password": "12345aa",
            "role": "customer",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_insensitive_email_failure(self):
        data = {
            "email": "Test@test.com",
            "username": "test",
            "password": "12345aa",
            "role": "customer",
        }

        email_with_dots_data = {
            "email": "te.st@test.com",
            "username": "test",
            "password": "12345aa",
            "role": "customer",
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(self.url, email_with_dots_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_failure(self):
        data = {
            "email": "test1@test.com",
            "username": "testuser",
            "password": "123",
            "role": "customer",
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_unconfirmed_after_success(self):
        pass
