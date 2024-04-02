from django.urls import path

from .views import LoginAPIView

urlpatterns = [
    path("api/v1/login/", LoginAPIView.as_view(), name="login"),
]
