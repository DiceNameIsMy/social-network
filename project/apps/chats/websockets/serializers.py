from rest_framework import serializers

from apps.chats.models import Message
from apps.chats.tasks import create_chat_message_notification


WEBOSCKET_MESSAGE_CHOICES = (
    (1, 'error'),
    (2, 'message'),
    (3, 'notification'),
)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['pk', 'chat', 'sender', 'username', 'datetime', 'text']

    def create(self, validated_data):
        """ Create message and send task to notificate chat members 
        """
        instance: Message = super().create(validated_data)
        create_chat_message_notification.delay(
            message_pk=instance.pk,
        )
        return instance


class WebsocketChatMessageContentSerializer(serializers.Serializer):
    """ Serializer for message from websocket
    """
    chat_id = serializers.IntegerField()
    text = serializers.CharField()

    def validate_chat_id(self, value):
        if value not in self.context['chat_ids']:
            raise serializers.ValidationError('user is not a member of a given chat')
    
