import re

from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from utitlities.utils import get_api_response

from .serializers import UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SignupAPIView(APIView):
    """
    A view for user signup.
    """

    def is_valid_email(self, email):
        """
        A function that checks if the provided email is valid or not.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def post(self, request):
        """
        Handles the POST request for user signup.
        Validates the input data, checks for existing email, converts email to lowercase,
        and creates a new user if all conditions are met.
        Returns an API response indicating success or failure of the signup process.
        """
        name = request.data.get("name")
        email = request.data.get("email")
        password = request.data.get("password")

        if not name:
            return get_api_response(
                False,
                {"message": "Please enter name!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if not email:
            return get_api_response(
                False,
                {"message": "Please enter email!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return get_api_response(
                False,
                {"message": "Please enter password!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if not self.is_valid_email(email):
            return get_api_response(
                False,
                {"message": "Please enter valid email!"},
                status.HTTP_400_BAD_REQUEST,
            )

        # Convert email to lowercase to match case-insensitive comparison
        email = email.lower()

        # Check if email is already registered with another user
        if User.objects.filter(email__iexact=email).exists():
            return get_api_response(
                False,
                {"message": "Email already registered with another user!"},
                status.HTTP_400_BAD_REQUEST,
            )

        # Create new user
        user_obj = User.objects.create_user(
            first_name=name, username=email, email=email, password=password
        )

        return get_api_response(
            True, {"message": "Signup successfully Completed!"}, status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginAPIView(APIView):
    """
    A view for user authentication.
    """

    def is_valid_email(self, email):
        """
        A function that checks if the provided email is valid or not.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def post(self, request):
        """
        A function that handles the POST request for user authentication.
        It takes a request object as a parameter.
        It retrieves the username and password from the request data.
        If either the username or password is missing or the email is not valid, it returns a specific error response.
        It then converts the username to lowercase for case-insensitive comparison.
        It attempts to authenticate the user with the provided credentials and handles the response accordingly.
        """
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not email:
            return get_api_response(
                False,
                {"message": "Please enter email!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return get_api_response(
                False,
                {"message": "Please enter password!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if not self.is_valid_email(email):
            return get_api_response(
                False,
                {"message": "Please enter valid email!"},
                status.HTTP_400_BAD_REQUEST,
            )

        # Convert username to lowercase to ensure case-insensitive comparison
        email = email.lower()

        # Authenticate the user using Django's authenticate function
        user = authenticate(username=email, password=password)

        if user is not None:
            # If the user is authenticated, log in the user and return a success response
            login(request, user)
            return get_api_response(
                True, {"message": "Login successful"}, status.HTTP_200_OK
            )
        else:
            return get_api_response(
                False,
                {"message": "Invalid credentials"},
                status.HTTP_401_UNAUTHORIZED,
            )


class LogoutAPIView(APIView):
    """
    A view for user logout.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return get_api_response(
            True, {"message": "Logout successful"}, status.HTTP_200_OK
        )


class SearchUserAPIView(APIView):
    """
    A view for searching users.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get(self, request):
        """
        A function to handle GET requests for searching users.
        Retrieves the search query from the request object. If no query is provided, returns a bad request response.
        Filters the User queryset based on the search query, excluding the current user. Orders the results by email.
        Paginates the queryset using the pagination class specified.
        Serializes the paginated queryset using the UserSerializer.
        Returns the paginated response.
        """
        search_query = request.GET.get("q")
        if not search_query:
            return get_api_response(
                False,
                {"message": "Please enter email or name to search."},
                status.HTTP_400_BAD_REQUEST,
            )

        # Filter the queryset based on the search query
        # Excluding the current user as we should only see other users in search
        # Checking if we find the exact match first, if not we check for partial matches
        users_queryset = User.objects.filter(Q(email__iexact=search_query)).exclude(
            id=self.request.user.id  # type: ignore
        )

        if not users_queryset.exists():
            users_queryset = (
                User.objects.filter(
                    Q(email__icontains=search_query)
                    | Q(first_name__icontains=search_query)
                )
                .exclude(id=self.request.user.id)  # type: ignore
                .order_by("email")
            )

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(users_queryset, request)

        serializer = UserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
