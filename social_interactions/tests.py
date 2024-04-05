from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from unittest.mock import patch

from .models import FriendRequest, Friend


class FriendRequestAPITest(APITestCase):
    URL = reverse("friend-request-api")

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="password"
        )

    def test_send_friend_request(self):
        # Set up
        self.client.force_authenticate(user=self.user1)  # type: ignore
        data = {"action": "send", "friend_id": self.user2.id}  # type: ignore

        # Test
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["response"]["message"], "Friend request sent successfully!")  # type: ignore

    def test_accept_friend_request(self):
        # Set up
        friend_request = FriendRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )
        self.client.force_authenticate(user=self.user2)  # type: ignore
        data = {"action": "accept", "friend_request_id": friend_request.id}  # type: ignore

        # Test
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["response"]["message"], "Friend request accepted successfully!"  # type: ignore
        )

    def test_reject_friend_request(self):
        # Set up
        friend_request = FriendRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )
        self.client.force_authenticate(user=self.user2)  # type: ignore
        data = {"action": "reject", "friend_request_id": friend_request.id}  # type: ignore

        # Test
        response = self.client.post(self.URL, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["response"]["message"], "Friend request rejected successfully!"  # type: ignore
        )

    def test_send_friend_request_throttling(self):
        self.friend1 = User.objects.create_user(
            username="friend1", email="friend1@example.com", password="testpassword"
        )
        self.friend2 = User.objects.create_user(
            username="friend2", email="friend2@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.friend1)  # type: ignore

        # Send 3 friend requests within 1 minute
        for _ in range(3):
            response = self.client.post(
                self.URL,
                {"action": "send", "friend_id": self.friend2.id},  # type: ignore
                format="json",
            )
            self.assertIn(response.status_code, [200, 400])

        # Attempt to send another friend request within 1 minute
        response = self.client.post(
            self.URL,
            {"action": "send", "friend_id": self.friend2.id},  # type: ignore
            format="json",
        )

        # Assert that the request is throttled
        self.assertEqual(response.status_code, 429)


class FriendListAPITest(APITestCase):
    URL = reverse("friend-list-api")

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="password"
        )
        self.friend1 = Friend.objects.create(friend1=self.user1, friend2=self.user2)

    def test_get_friend_list(self):
        # Set up
        self.client.force_authenticate(user=self.user1)  # type: ignore

        # Test
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)  # type: ignore
        self.assertEqual(response.data["results"][0]["id"], self.user2.id)  # type: ignore

    def test_pagination(self):
        # Set up
        count = 15
        self.new_test_user = User.objects.create_user(
            username="new_user_test",
            email="new_user_test@example.com",
            password="password",
        )
        users = [
            User.objects.create_user(
                username=f"user{i}@example.com",
                email=f"user{i}@example.com",
                password="password",
            )
            for i in range(30, 30 + count)
        ]
        friends = [
            Friend.objects.create(friend1=self.new_test_user, friend2=user)
            for user in users
        ]
        self.client.force_authenticate(user=self.new_test_user)  # type: ignore

        # Test
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], count)  # type: ignore

    def test_authenticated_user_access(self):
        # Test unauthenticated access
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403)

        # Test authenticated access
        self.client.force_authenticate(user=self.user1)  # type: ignore
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)


class PendingFriendListAPITest(APITestCase):
    URL = reverse("pending-friend-requests")

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="password"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="password"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="password"
        )
        self.friend_request1 = FriendRequest.objects.create(
            from_user=self.user1, to_user=self.user2, accepted=False
        )
        self.friend_request2 = FriendRequest.objects.create(
            from_user=self.user3, to_user=self.user1, accepted=False
        )

    def test_get_pending_friend_list(self):
        # Set up
        self.client.force_authenticate(user=self.user1)  # type: ignore

        # Test
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)  # type: ignore

    def test_pagination(self):
        # Set up
        count = 10
        self.test_user = User.objects.create_user(
            username="user_test", email="user_test@example.com", password="password"
        )
        users = [
            User.objects.create_user(
                username=f"user{i}@example.com",
                email=f"user{i}@example.com",
                password="password",
            )
            for i in range(50, 50 + count)
        ]
        friend_requests = [
            FriendRequest.objects.create(
                from_user=user, to_user=self.test_user, accepted=False
            )
            for user in users
        ]
        self.client.force_authenticate(user=self.test_user)  # type: ignore

        # Test
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], count)  # type: ignore

    def test_authenticated_user_access(self):
        # Test unauthenticated access
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 403)

        # Test authenticated access
        self.client.force_authenticate(user=self.user1)  # type: ignore
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
