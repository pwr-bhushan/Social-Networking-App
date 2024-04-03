from django.contrib.auth.models import User

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name"]

    # Override to_representation for the 'id' field
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["id"] = int(representation["id"]) + 100000
        representation["name"] = representation.pop("first_name")
        return representation
