from django.contrib.auth.models import User

from rest_framework.test import APITestCase


class SignupAPIViewTests(APITestCase):
    URL = "/user/api/v1/signup/"

    def test_signup_success(self):
        """
        Test successful user signup.
        """
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        }
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")

    def test_signup_missing_name(self):
        """
        Test signup with missing name.
        """
        data = {"email": "test@example.com", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["response"]["message"], "Please enter name!")  # type: ignore

    def test_signup_missing_email(self):
        """
        Test signup with missing email.
        """
        data = {"name": "Test User", "password": "password123"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["response"]["message"], "Please enter email!")  # type: ignore

    def test_signup_missing_password(self):
        """
        Test signup with missing password.
        """
        data = {"name": "Test User", "email": "test@example.com"}
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["response"]["message"], "Please enter password!")  # type: ignore

    def test_signup_invalid_email(self):
        """
        Test signup with invalid email.
        """
        data = {
            "name": "Test User",
            "email": "invalid_email",
            "password": "password123",
        }
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["response"]["message"], "Please enter valid email!"  # type: ignore
        )

    def test_signup_existing_email(self):
        """
        Test signup with existing email.
        """
        User.objects.create_user(
            first_name="Test User",
            username="existing@example.com",
            email="existing@example.com",
            password="password123",
        )
        data = {
            "name": "Test User",
            "email": "existing@example.com",
            "password": "password123",
        }
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["response"]["message"],  # type: ignore
            "Email already registered with another user!",
        )


class LoginAPITestCase(APITestCase):
    URL = "/user/api/v1/login/"

    def setUp(self):
        """
        Set up the test environment by creating a user with the given username, email, and password.
        """
        self.user = User.objects.create_user(
            first_name="Test User",
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


class SearchUserAPIViewTest(APITestCase):
    URL = "/user/api/v1/search/"

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            first_name="Test User",
            username="testuser",
            email="test@example.com",
            password="password",
        )
        self.client.force_authenticate(user=self.user)  # type: ignore

    def test_search_user_with_query_exact_match(self):
        # Test searching for a user with an exact email match
        query = "test@example.com"
        response = self.client.get(self.URL, {"q": query})
        self.assertEqual(response.status_code, 200)

    def test_search_user_with_query_partial_match(self):
        # Test searching for a user with a partial email match
        query = "test"
        response = self.client.get(self.URL, {"q": query})
        self.assertEqual(response.status_code, 200)

    def test_search_user_without_query(self):
        # Test searching for a user without a query
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 400)

    def test_search_user_nonexistent_query(self):
        # Test searching for a user with a query that does not match any user
        query = "nonexistent@example.com"
        response = self.client.get(self.URL, {"q": query})
        self.assertEqual(response.status_code, 200)

    def test_search_user_pagination(self):
        # Test pagination of search results
        query = "test"
        response = self.client.get(self.URL, {"q": query})
        self.assertEqual(response.status_code, 200)

    def test_search_user_correct_number_of_users(self):
        # Verify that the response contains the correct number of users
        # Create more users for testing
        for i in range(15):
            User.objects.create_user(
                first_name=f"User {i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password",
            )

        query = "user"
        response = self.client.get(self.URL, {"q": query})
        self.assertEqual(response.status_code, 200)

        # Calculate the expected number of users based on the queryset
        queryset = User.objects.filter(email__icontains=query).exclude(id=self.user.id)  # type: ignore
        expected_users_count = queryset.count()

        # Check if the number of users in the response matches the expected count
        self.assertEqual(response.data["count"], expected_users_count)  # type: ignore
