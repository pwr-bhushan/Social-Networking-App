from django.urls import path

from .views import SignupAPIView, LoginAPIView, LogoutAPIView, SearchUserAPIView

urlpatterns = [
    path("api/v1/signup/", SignupAPIView.as_view(), name="signup"),
    path("api/v1/login/", LoginAPIView.as_view(), name="login"),
    path("api/v1/logout/", LogoutAPIView.as_view(), name="logout"),
    path("api/v1/search/", SearchUserAPIView.as_view(), name="user_search"),
]
