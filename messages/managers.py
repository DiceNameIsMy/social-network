from fastapi import WebSocket

from models import User, UserConnection, Chat
from utils import send_api_request


class Connection:
    """ Connection to chat
    """
    def __init__(self, chat: Chat):
        self.chat = chat
        self.users: list[UserConnection] = []

    async def connect(
        self, 
        user: User, 
        websocket: WebSocket
    ) -> UserConnection:
        user_connection = UserConnection(
            user=user,
            chat=self.chat,
            websocket=websocket
        )
        self.users.append(user_connection)

        return user_connection

    async def disconnect(self, user_connection: UserConnection):
        await user_connection.websocket.close()
        self.users.remove(user_connection)

        if not self.users:
            del self

    async def send_message(
        self, 
        user: User, 
        message: str
    ):
        r = send_api_request(
            method='POST',
            url=f'/api/v1/chats/{self.chat.pk}/messages/',
            user=user,
            data={"text": message},
        )
        data = r.json()
        if r.status_code != 201:
            raise NotImplementedError('not `201` status code behavior is not implementet')

        message = {
            'type': 'message',
            'content': data
        }

        for user_connection in self.users:
            await user_connection.websocket.send_json(message)


class ConnectionsManager:
    """ Manages connections to chats
    """
    def __init__(self) -> None:
        self.chats: dict[int, Connection] = {}

    def get_chat_connection(self, chat: Chat) -> Connection:
        if chat.pk not in self.chats:
            self.chats[chat.pk] = Connection(chat)

        return self.chats[chat.pk]
        


