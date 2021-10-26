from django.db import models

from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model


UserModel = get_user_model()

class MembershipType(models.IntegerChoices):
    ADMIN = 1
    REGULAR = 2

class ChatType(models.IntegerChoices):
    COMMON = 1
    DIRECT = 2


class Chat(models.Model):
    Type = ChatType

    type = models.PositiveIntegerField(
        choices=Type.choices,
        default=Type.COMMON,
        editable=False
    )
    title = models.CharField(
        max_length=64,
    )

    def members_amount(self):
        return self.memberships.count()

    def __str__(self) -> str:
        return self.title


class Membership(models.Model):
    Type = MembershipType

    type = models.PositiveIntegerField(
        choices=Type.choices,
        default=Type.REGULAR,
    )
    user = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    def clean(self):
        if self.chat.type == ChatType.DIRECT:
            self.type = self.Type.ADMIN

    def __str__(self) -> str:
        return self.chat.title


class Message(models.Model):
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    datetime = models.DateTimeField(auto_now_add=True)
    text = models.CharField(
        max_length=512,
        blank=True
    )
    class Meta:
        ordering = ['-datetime']


    def clean(self):
        user_ids = self.chat.memberships.all().values_list('user_id', flat=True)
        if self.sender.id not in user_ids:
            raise ValidationError(
                f'message sender should be a chat member'
            )
    
    def date(self):
        return self.datetime.date()

    def __str__(self) -> str:
        return f'{self.sender.username}: {self.date()}'



