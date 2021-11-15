from rest_framework import serializers

from apps.chats.models import Message
from apps.chats.tasks import create_chat_message_notification


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['pk', 'chat', 'sender', 'username', 'datetime', 'text']

    def create(self, validated_data):
        """ Create message and send task to notificate chat members 
        """
        instance: Message = super().create(validated_data)
        create_chat_message_notification(
            message=instance,
        )
        return instance

