from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class LoginAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone="9800000001",
            full_name="Test Patient",
            role="patient",
            password="StrongPass123"
        )
        self.login_url = "/api/auth/login/"

    def test_UT01_login_with_correct_credentials(self):
        response = self.client.post(self.login_url, {
            "identifier": "9800000001",
            "password": "StrongPass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data["data"])

    def test_UT02_login_with_wrong_password(self):
        response = self.client.post(self.login_url, {
            "identifier": "9800000001",
            "password": "WrongPassword"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "INVALID_CREDENTIALS")

    def test_UT03_login_with_unregistered_phone(self):
        response = self.client.post(self.login_url, {
            "identifier": "9899999999",
            "password": "AnyPassword"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["code"], "INVALID_CREDENTIALS")