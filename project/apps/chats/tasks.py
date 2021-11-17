from asgiref.sync import async_to_sync

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from celery import shared_task

from channels.layers import channel_layers
from channels import DEFAULT_CHANNEL_LAYER
from channels_redis.core import RedisChannelLayer
from django.utils import timezone

from apps.accounts.models import CustomUser, Notification
from apps.chats.models import Chat, Message

from apps.accounts.api.v1.serializers import NotificationSerializer

channel_layer: RedisChannelLayer = channel_layers[DEFAULT_CHANNEL_LAYER]


@shared_task
def create_chat_message_notification(
    message_pk: int
):
    """
    Create notification and send it to online users
    """
    message = Message.objects.get(pk=message_pk)
    chat_members = message.chat.members.all()
    chat_content_type = ContentType.objects.get_for_model(message.chat)
    chat_notifications = Notification.objects.filter(
        content_type=chat_content_type, 
        object_id=message.chat.pk
    )
    for member in chat_members:
        if member.pk == message.sender_id:
            continue
    
        member_online = cache.get(f"user_{member.pk}_online", False)
        if member_online:
            continue
        
        notification, created = chat_notifications.get_or_create(
            user=member,
            defaults={
                'user': member,
                'type': Notification.Type.CHAT_MESSAGE,
                'content_type': chat_content_type,
                'object_id': message.chat.pk,
                'data': {
                    'messages': []
                }
            }
        )
        # Update or set message data
        notification.data['messages'].append({
            'sender': message.username(),
            'text': message.text,
            'date': str(message.datetime),
        })
        notification.created_at = timezone.now()
        notification.save()
        return True
