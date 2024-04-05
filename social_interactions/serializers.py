from rest_framework import serializers

from user_operations.serializers import UserSerializer

from .models import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for FriendRequest model.
    """

    from_user = UserSerializer()
    to_user = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ["id", "from_user", "to_user"]
