from django.contrib.auth.models import User

from rest_framework.test import APITestCase


class SignupAPIViewTests(APITestCase):
    URL = "/user/api/v1/signup/"

    def test_signup_success(self):
        """
        Test successful user signup.
        """
        data = {"email": "test@example.com", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")

    def test_signup_missing_email(self):
        """
        Test signup with missing email.
        """
        data = {"password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["response"]["message"], "Please enter email!")

    def test_signup_missing_password(self):
        """
        Test signup with missing password.
        """
        data = {"email": "test@example.com"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["response"]["message"], "Please enter password!")

    def test_signup_invalid_email(self):
        """
        Test signup with invalid email.
        """
        data = {"email": "invalid_email", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["response"]["message"], "Please enter valid email!"
        )

    def test_signup_existing_email(self):
        """
        Test signup with existing email.
        """
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="password123",
        )
        data = {"email": "existing@example.com", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["response"]["message"],
            "Email already registered with another user!",
        )


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
        data = {"email": "test@example.com", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_login_api_with_invalid_credentials(self):
        """
        Test the login API with invalid credentials.
        """
        data = {"email": "test@example.com", "password": "wrongpassword"}
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
        data = {"email": "test@example.com"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_api_with_invalid_email(self):
        """
        Test the login API with invalid email format.
        """
        data = {"email": "invalidemail", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_login_api_with_valid_credentials_in_uppercase(self):
        """
        Test the login API with valid credentials in uppercase.
        """
        data = {"email": "TEST@EXAMPLE.COM", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_login_api_with_valid_credentials_in_mixcase(self):
        """
        Test the login API with valid credentials in mixed case.
        """
        data = {"email": "TEST@example.COM", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)
