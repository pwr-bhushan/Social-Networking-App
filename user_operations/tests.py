from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class LoginAPITestCase(APITestCase):
    URL = "/user/api/v1/login/"

    def setUp(self):
        """
        Set up the test environment by creating a user with the given username, email, and password.
        """
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="password123",
        )

    def test_login_api_with_valid_credentials(self):
        """
        Test the login API with valid credentials.
        """
        data = {"username": "test@example.com", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_login_api_with_invalid_credentials(self):
        """
        Test the login API with invalid credentials.
        """
        data = {"username": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_login_api_with_missing_username(self):
        """
        Test the login API when username is missing.
        """
        data = {"password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_api_with_missing_password(self):
        """
        Test the login API when password is missing.
        """
        data = {"username": "test@example.com"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_api_with_invalid_email(self):
        """
        Test the login API with invalid email format.
        """
        data = {"username": "invalidemail", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_api_with_valid_credentials_in_uppercase(self):
        """
        Test the login API with valid credentials in uppercase.
        """
        data = {"username": "TEST@EXAMPLE.COM", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_login_api_with_valid_credentials_in_mixcase(self):
        """
        Test the login API with valid credentials in mixed case.
        """
        data = {"username": "TEST@example.COM", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)
