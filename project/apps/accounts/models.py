from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class NotificationType(models.IntegerChoices):
    CHAT_MESSAGE = 1
    FRIEND_REQUEST = 2


class CustomUser(AbstractUser):
    friends = models.ManyToManyField(
        to='self',
        blank=True,
        related_name='friends'
    )
    friend_requests = models.ManyToManyField(
        to='self',
        blank=True,
        related_name='friend_request'
    )
    def friends_amount(self) -> int:
        return self.friends.count()


class Notification(models.Model):
    Type = NotificationType
    content_type_limit = (
        models.Q(app_label='accounts', model='customuser') |
        models.Q(app_label='chats', model='chat')
    )

    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.IntegerField(
        choices=Type.choices,
    )
    data = models.JSONField(default=dict)
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=content_type_limit
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.user} - {self.content_object}'

    class Meta:
        ordering = ['-created_at'] # newest first
        indexes = [
            models.Index(
                fields=['user', 'is_read'], 
                condition=models.Q(is_read=False),
                name='index_unread_notifications'
            )
        ]