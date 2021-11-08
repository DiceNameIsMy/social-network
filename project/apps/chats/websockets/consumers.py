import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.chats.models import Chat, Membership, Message
from apps.chats.api.v1.serializers import RoutingMessageSerializer


UserModel = get_user_model()


class ChatConsumer(WebsocketConsumer):
    token: AccessToken = None
    chat_id: int = None
    user: UserModel = None
    chat: Chat = None
    
    errors = []

    def authenticate(self) -> bool:
        """ Authenticate user and return bool when 
        token is valid and user has access to chat
        """
        try:
            self.token = AccessToken(self.query_params.get('token'))
            self.user = get_object_or_404(
                UserModel, 
                pk=self.token.payload['user_id']
            )
            return self.is_chat_member()
        except TokenError:
            self.errors
            return False
        except UserModel.DoesNotExist:
            return False

    def is_chat_member(self) -> bool:
        """ Validates that user is a member of a chat
        """
        try:
            chat = Chat.objects.prefetch_related('members').get(pk=self.chat_id)
        except Chat.DoesNotExist:
            self.errors.append(f'chat with pk={self.chat_id} does not exist')
            return False
        else:
            self.chat = chat
            is_chat_member = self.user in chat.members.all()

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
        if not self.authenticate():
            self.send(json.dumps({
                'type': 'error',
                'content': self.errors
            }))
            self.close()
            return
        
        # Join chat group
        async_to_sync(self.channel_layer.group_add)(
            self.chat_id,
            self.channel_name
        )

    def disconnect(self, close_code):
        # Leave chat group
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id,
            self.channel_name
        )

    def receive(self, text_data=None):
        """ Recieve message from client.
        """
        data = json.loads(text_data)
        
        serializer = RoutingMessageSerializer(data={
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
            self.chat_id,
            message_data
        )

    def message(self, event):
        """ called when new message was sent by other user
        """
        # Send message to client
        self.send(text_data=json.dumps(event))
