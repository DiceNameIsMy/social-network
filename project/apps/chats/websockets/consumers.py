import json

from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from channels.generic.websocket import WebsocketConsumer
from channels_redis.core import RedisChannelLayer

from apps.chats.models import Chat, Membership, Message
from apps.chats.api.v1.serializers import MessageSerializer

from .exceptions import WebSocketException, EmptyFieldException


UserModel = get_user_model()


class ChatConsumer(WebsocketConsumer):
    channel_layer: RedisChannelLayer

    raw_token: str = None
    user_pk: int = None
    chat_id: int = None

    token: AccessToken = None
    user: UserModel = None
    chat: Chat = None


    def connect(self):
        self.accept()
        self.set_connection_parameters()

        if self.has_permission():
            cache.set(f"user_{self.user.pk}_online", True)
            async_to_sync(self.channel_layer.group_add)(
                f'chat_{self.chat.pk}',
                self.channel_name
            )
        else:
            self.close()

    def disconnect(self, close_code):
        if self.user and self.chat:
            cache.set(f"user_{self.user.pk}_online", False)
            async_to_sync(self.channel_layer.group_discard)(
                f'chat_{self.chat.pk}',
                self.channel_name
            )

    def receive(self, text_data):
        """ Receive message from client.
        """
        data = json.loads(text_data)

        try:
            data_type = data['type']
            if data_type == 'message':
                self.send_message(data['content'])
            else:
                self.send_error(f'unknown message type: {data_type}')
        except KeyError:
            self.send_error('unvalid request body')

    def send_message(self, message: str):
        """ client sent a message
        """
        serializer = MessageSerializer(data={
            'chat': self.chat.pk,
            'sender': self.user.pk,
            'text': message
        })
        if not serializer.is_valid():
            self.error_message = serializer.errors
            self.send_error(str(serializer.errors))
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

    def has_permission(self) -> bool:
        try:
            self.authenticate()
            self.is_chat_member()
            return True
        except (WebSocketException, TokenError) as e:
            self.send_error(e)
        except UserModel.DoesNotExist as e:
            self.send_error('User was not found')
        except Chat.DoesNotExist as e:
            self.send_error('Chat was not found')
        finally:
            return False

    def authenticate(self):
        """ Authenticate user
        """
        if not self.raw_token:
            raise EmptyFieldException('token')

        self.token = AccessToken(self.raw_token)
        user_pk = self.token.payload.get('user_id')
        self.user = UserModel.objects.get( 
            pk=user_pk
        )

    def is_chat_member(self):
        """ Validates that user is a member of a chat
        """
        chat = Chat.objects.prefetch_related('members').get(pk=self.chat_id)
        self.chat = chat

        is_chat_member = self.user in chat.members.all()
        if not is_chat_member:
            raise WebSocketException(
                f'user is not a member of this chat'
            )

    def send_error(self, message: str):
        """ send error message to client
        """
        self.send(json.dumps({
            'type': 'error',
            'content': str(message)
        }))

    def set_connection_parameters(self):
        """ Called on connection
        """
        self.query_params = dict(
            param.split('=') for param in self.scope['query_string'].decode().split('&') if param
        )
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.raw_token = self.query_params.get('token')

    def message(self, event):
        """ new message was recieved
        """
        self.send(text_data=json.dumps(event))
