from django.urls import path

from .views import FriendRequestAPI, FriendListAPI, PendingFriendListAPI

urlpatterns = [
    path(
        "api/v1/friend-request/", FriendRequestAPI.as_view(), name="friend-request-api"
    ),
    path("api/v1/friends/", FriendListAPI.as_view(), name="friend-list-api"),
    path(
        "api/v1/pending-friend-requests/",
        PendingFriendListAPI.as_view(),
        name="pending-friend-requests",
    ),
]
