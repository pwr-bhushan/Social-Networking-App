from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        related_name="sent_friend_requests",
        on_delete=models.CASCADE,
        help_text="The user who sent the friend request.",
    )
    to_user = models.ForeignKey(
        User,
        related_name="received_friend_requests",
        on_delete=models.CASCADE,
        help_text="The user who received the friend request.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when the friend request was sent.",
    )
    accepted = models.BooleanField(
        default=False,
        help_text="Indicates whether the friend request has been accepted.",
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the friend request was accepted, if accepted.",
    )
    rejected = models.BooleanField(
        default=False,
        help_text="Indicates whether the friend request has been rejected.",
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the friend request was rejected, if rejected.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Friend Request"
        verbose_name_plural = "Friend Requests"
        unique_together = ("from_user", "to_user")


class Friend(models.Model):
    friend1 = models.ForeignKey(
        User,
        related_name="friend1",
        on_delete=models.CASCADE,
        help_text="One of the users who are friends.",
    )
    friend2 = models.ForeignKey(
        User,
        related_name="friend2",
        on_delete=models.CASCADE,
        help_text="The other user who is friends with the first user.",
    )

    class Meta:
        verbose_name = "Friends"
        verbose_name_plural = "Friends"
        unique_together = ("friend1", "friend2")
