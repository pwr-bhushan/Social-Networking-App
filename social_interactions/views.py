from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


from utitlities.utils import get_api_response
from user_operations.serializers import UserSerializer

from .models import FriendRequest, Friend
from .serializers import FriendRequestSerializer


class FriendRequestAPI(APIView):
    """
    API endpoint for managing friend requests.
    """

    permission_classes = [IsAuthenticated]

    ACTIONS = {
        "send": "handle_send",
        "accept": "handle_accept",
        "reject": "handle_reject",
    }

    def handle_send(self, request, *args, **kwargs):
        """
        Handles sending a friend request.
        """
        user = request.user
        request_count_key = f"request_count:{user.id}"
        timestamp_key = f"timestamp:{user.id}"

        # Get the current timestamp
        current_time = timezone.now()

        # Check if the user has exceeded the rate limit
        request_count = cache.get(request_count_key, 0)
        last_request_timestamp = cache.get(timestamp_key)

        if last_request_timestamp is not None:
            time_difference = current_time - last_request_timestamp
            if time_difference.total_seconds() < 60:
                if request_count >= 3:
                    return (
                        False,
                        {"message": "You can send only 3 requests per minute!"},
                        status.HTTP_429_TOO_MANY_REQUESTS,
                    )

        # Increment the request count and update the timestamp
        cache.set(request_count_key, request_count + 1, timeout=60)
        cache.set(timestamp_key, current_time, timeout=60)

        friend_obj = kwargs.get("friend_obj")

        # Check if friend request already sent
        if (
            FriendRequest.objects.filter(
                Q(from_user=request.user, to_user=friend_obj)
                | Q(from_user=friend_obj, to_user=request.user)
            )
            .filter(rejected=False)
            .exists()
        ):
            return (
                False,
                {"message": "Friend request already sent!"},
                status.HTTP_400_BAD_REQUEST,
            )

        # Check if friend request already accepted
        if Friend.objects.filter(
            Q(friend1=request.user, friend2=friend_obj)
            | Q(friend1=friend_obj, friend2=request.user)
        ).exists():
            return (
                False,
                {"message": "Friend request already accepted!"},
                status.HTTP_400_BAD_REQUEST,
            )

        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=friend_obj,
            created_at=timezone.now(),
        )
        return (
            True,
            {"message": "Friend request sent successfully!"},
            status.HTTP_200_OK,
        )

    def handle_accept(self, request, *args, **kwargs):
        """
        Handles accepting a friend request.
        """
        friend_request_id = kwargs.get("friend_request_id")
        friend_request = FriendRequest.objects.filter(id=friend_request_id).first()

        if friend_request and friend_request.to_user == request.user:
            friend_request.accepted = True
            friend_request.accepted_at = timezone.now()
            friend_request.save()

            friend = Friend.objects.create(
                friend1=friend_request.from_user,
                friend2=friend_request.to_user,
            )

            return (
                True,
                {"message": "Friend request accepted successfully!"},
                status.HTTP_200_OK,
            )
        else:
            return (
                False,
                {"message": "Friend request not found!"},
                status.HTTP_404_NOT_FOUND,
            )

    def handle_reject(self, request, *args, **kwargs):
        """
        Handles rejecting a friend request.
        """
        friend_request_id = kwargs.get("friend_request_id")
        friend_request = FriendRequest.objects.filter(id=friend_request_id).first()

        if friend_request and friend_request.to_user == request.user:
            friend_request.rejected = True
            friend_request.rejected_at = timezone.now()
            friend_request.save()

            return (
                True,
                {"message": "Friend request rejected successfully!"},
                status.HTTP_200_OK,
            )
        else:
            return (
                False,
                {"message": "Friend request not found!"},
                status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        """
        Handles POST requests to manage friend requests.
        """
        action = request.data.get("action")
        friend_id = request.data.get("friend_id")
        friend_request_id = request.data.get("friend_request_id")

        if not action:
            return get_api_response(
                False,
                {"message": "Please enter action!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if action not in ["send", "accept", "reject"]:
            return get_api_response(
                False,
                {"message": "Please enter valid action!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if action == "send" and not friend_id:
            return get_api_response(
                False,
                {"message": "Please select friend!"},
                status.HTTP_400_BAD_REQUEST,
            )

        if action in ["accept", "reject"] and not friend_request_id:
            return get_api_response(
                False,
                {"message": "Please select friend request!"},
                status.HTTP_400_BAD_REQUEST,
            )

        friend_obj = None
        if friend_id:
            friend_obj = User.objects.filter(id=friend_id).first()
            if not friend_obj:
                return get_api_response(
                    False,
                    {"message": "Please select valid friend!"},
                    status.HTTP_400_BAD_REQUEST,
                )

        is_valid, response, resp_status = getattr(self, self.ACTIONS[action])(
            request, friend_obj=friend_obj, friend_request_id=friend_request_id
        )

        return get_api_response(
            is_valid,
            response,
            resp_status,
        )


class FriendListAPI(APIView):
    """
    API endpoint for getting friend list.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get(self, request):
        """
        Handles GET requests to get friend list.
        """
        # Get user IDs of friends
        friend_ids = Friend.objects.filter(
            Q(friend1=request.user) | Q(friend2=request.user)
        ).values_list("friend1_id", "friend2_id")

        # Flatten the list of IDs and exclude current user's ID
        friend_ids = [
            friend_id
            for friend_tuple in friend_ids
            for friend_id in friend_tuple
            if friend_id != request.user.id
        ]

        # Fetch friends from User queryset
        friend_list = User.objects.filter(id__in=friend_ids).order_by("email")

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(friend_list, request)

        serializer = UserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class PendingFriendListAPI(APIView):
    """
    API endpoint for getting friend list.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get(self, request):
        """
        Handles GET requests to get friend list.
        """
        # Retrieve pending friend requests involving the current user
        pending_friend_requests = FriendRequest.objects.filter(
            Q(from_user=request.user, accepted=False)
            | Q(to_user=request.user, accepted=False)
        ).exclude(Q(rejected=True) | Q(accepted=True))

        # Apply pagination
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(
            pending_friend_requests, request
        )

        serializer = FriendRequestSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
