import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model
from django.core.cache import cache

from channels_redis.core import RedisChannelLayer

from apps.chats.models import Chat, Membership, Message
from apps.chats.api.v1.serializers import MessageSerializer


UserModel = get_user_model()


class ChatConsumer(WebsocketConsumer):
    channel_layer: RedisChannelLayer
    token: AccessToken = None
    user: UserModel = None
    chat_id: int = None
    chat: Chat = None
    
    errors = []

    def has_permission(self) -> bool:
        is_authenticated = self.authenticate()
        is_chat_member = self.is_chat_member()
        return (is_authenticated and is_chat_member)

    def authenticate(self) -> bool:
        """ Authenticate user
        """
        try:
            self.token = AccessToken(self.query_params.get('token'))
            self.user = UserModel.objects.get( 
                pk=self.token.payload['user_id']
            )
            return True
        except TokenError:
            self.errors.append('invalid token')
            return False
        except UserModel.DoesNotExist:
            self.errors.append(f'user with pk={self.user.pk} does not exist')
            return False

    def is_chat_member(self) -> bool:
        """ Validates that user is a member of a chat
        """
        try:
            chat = Chat.objects.prefetch_related('members').get(pk=self.chat_id)
        except Chat.DoesNotExist:
            self.errors.append(f'chat with pk={self.chat_id} does not exist')
            return False
    
        self.chat = chat
        is_chat_member = self.user in chat.members.all()
        if not is_chat_member:
            self.errors.append(f'user with pk={self.user.pk} is not a member of chat with pk={self.chat_id}')

        return is_chat_member

    def send_errors(self):
        """ send error messages to client
        """
        self.send(json.dumps({
            'type': 'error',
            'content': self.errors
        }))

    def connect(self):
        self.accept()
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.query_params = dict(
            param.split('=') for param in self.scope['query_string'].decode().split('&') if param
        )
        if not self.has_permission():
            self.send_errors()
            self.close()
            return

        cache.set(f"user_{self.user.pk}_online", True)
        # Join chat group
        async_to_sync(self.channel_layer.group_add)(
            f'chat_{self.chat.pk}',
            self.channel_name
        )

    def disconnect(self, close_code):
        # Leave chat group
        cache.set(f"user_{self.user.pk}_online", False)
        async_to_sync(self.channel_layer.group_discard)(
            f'chat_{self.chat.pk}',
            self.channel_name
        )

    def receive(self, text_data=None):
        """ Recieve message from client.
        """
        data = json.loads(text_data)
        
        serializer = MessageSerializer(data={
            'chat': self.chat.pk,
            'sender': self.user.pk,
            'text': data['content']
        })

        if not serializer.is_valid():
            self.errors += list(serializer.errors.values())
            self.send_errors()
            return
    
        serializer.save()
        message_data = {
            'type': 'message',
            'content': serializer.data
        }
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            f'chat_{self.chat.pk}',
            message_data
        )

    def message(self, event):
        """ called when new message was sent by other user
        """
        # Send message to client
        self.send(text_data=json.dumps(event))
