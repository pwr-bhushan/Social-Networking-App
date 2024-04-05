from django.contrib.auth.models import User

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["name"] = representation.pop("first_name")
        return representation
