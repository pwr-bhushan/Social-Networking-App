import re

from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.views import APIView

from .utils import get_api_response


class LoginAPIView(APIView):

    def is_valid_email(self, email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def post(self, request):
        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username:
            return get_api_response(
                False,
                {"message": "Please enter username!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return get_api_response(
                False,
                {"message": "Please enter password!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.is_valid_email(username):
            return get_api_response(
                False,
                {"message": "Please enter valid email!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert username to lowercase to ensure case-insensitive comparison
        username = username.lower()

        user = authenticate(username=username, password=password)

        if user is not None:
            print("Login successful")
            login(request, user)
            return get_api_response(
                True, {"message": "Login successful"}, status=status.HTTP_200_OK
            )
        else:
            return get_api_response(
                False,
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
