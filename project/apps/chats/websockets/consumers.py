import json

from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import DenyConnection

from channels_redis.core import RedisChannelLayer

from apps.chats.models import Chat
from .serializers import MessageSerializer, WebsocketChatMessageContentSerializer


UserModel = get_user_model()


MESSAGE_TYPES = {
    'MESSAGE': 'chat_message',
    'ERROR': 'message_error'
}
MSG_FORMAT = {
    'type': MESSAGE_TYPES['MESSAGE'],
    'content': ''
}
ERROR_FORMAT = {
    'type': 'message_error',
    'content': ''
}

class ChatConsumer(WebsocketConsumer):
    channel_layer: RedisChannelLayer

    user_online_prefix = settings.REDIS_GROUPS_PREFIXES['ONLINE_USERS']
    chat_prefix = settings.CHANNEL_GROUPS_PREFIXES['CHAT']

    message_serializer = MessageSerializer

    raw_token: str = None
    user_pk: int = None
    chat_pk: int = None

    token: AccessToken
    user: UserModel
    chat: Chat

    def connect(self):
        self.init_connection()
        self.set_user_online(True)
        # group adding happens here because DenyConnection
        # is not being catched in websocket_connection
        for membership in self.memberships:
            group_name = f'{self.chat_prefix}{membership.chat.pk}'
            async_to_sync(self.channel_layer.group_add)(
                group_name,
                self.channel_name
            )
            self.groups.append(group_name)
        self.accept()

    def disconnect(self, code):
        self.set_user_online(False)

    def receive(self, text_data=None):
        """
        recieve message from client
        """
        # TODO decompose this method
        data = json.loads(text_data)
        try:
            message_type = data['type']
            if message_type == MESSAGE_TYPES['MESSAGE']:
                chat_ids = [m.chat.pk for m in self.memberships]
                serializer = WebsocketChatMessageContentSerializer(data=data['content'], context={'chat_ids': chat_ids})
                if serializer.is_valid():
                    self.send_text_message(data['content'])
                else:
                    self.send_error_message(serializer.errors)

            elif message_type == MESSAGE_TYPES['ERROR']:
                self.send_error_message('Unsupported message type')
            else:
                print(f'Unknown message type: {message_type}')
                self.send_error_message('Unknown message type')
        except KeyError:
            self.send_error_message('message body is not valid')

    # methods used when recieveing signals from groups
    def chat_message(self, message):
        self.send(text_data=json.dumps(message))
    # 

    def send_text_message(self, content: dict):
        """
        attempts to create a message and send it to the chat.
        will return an error message to a client otherwise
        """
        serializer = self.get_message_serializer(content)
        if not serializer.is_valid():
            self.send_error_message(serializer.errors)
            return
    
        serializer.save()
        msg_content = MSG_FORMAT.copy()
        msg_content['content'] = serializer.data

        async_to_sync(self.channel_layer.group_send)(
            f'{self.chat_prefix}{content["chat_id"]}',
            msg_content
        )

    def send_error_message(self, message: str):
        data = ERROR_FORMAT.copy()
        data['content'] = message
        self.send(json.dumps(data))

    def set_user_online(self, status: bool):
        """ 
        sets user online status in cache to decide 
        wrether to create a notification or not
        """
        cache.set(f'{self.user_online_prefix}{self.user_pk}', status)

    def get_message_serializer(self, content: dict):
        serializer = self.message_serializer(data={
            'chat': content['chat_id'],
            'sender': self.user.pk,
            'text': content['text']
        })
        return serializer

    def init_connection(self):
        """ 
        Initializes connection.
        raises DenyConnection if connection is not allowed.
        """
        query_string = self.scope['query_string'].decode()
        self.query_params = dict(
            param.split('=') for param in query_string.split('&') if param
        )
        self.raw_token = str(self.query_params.get('token'))

        self.token = self._get_token()
        self.user = self._get_user()
        self.memberships = self._get_memberships()

    def _get_token(self):
        try:
            token = AccessToken(self.raw_token)
            self.user_pk = token.payload['user_id']
        except TokenError as e:
            raise DenyConnection(e)
        except KeyError:
            raise DenyConnection('Token is not valid')

        return token
    
    def _get_user(self):
        try:
            user = UserModel.objects.get(pk=self.user_pk)
        except UserModel.DoesNotExist:
            raise DenyConnection('Token is not valid')
        return user
    
    def _get_chat(self):
        try:
            chat = Chat.objects.prefetch_related('memberships').get(pk=self.chat_pk)
            chat_memebers_ids = chat.memberships.values_list('user_id', flat=True)

            if not (self.user_pk in chat_memebers_ids):
                raise DenyConnection('User is not a member of this chat')
        except Chat.DoesNotExist:
            raise DenyConnection('User is not a member of this chat')
        return chat
    
    def _get_memberships(self):
        return self.user.memberships.select_related('chat').all()

