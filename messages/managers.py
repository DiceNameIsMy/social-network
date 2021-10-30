from fastapi import WebSocket

from requests import request

from settings import settings

from models import User, UserConnection, Chat


class Connection:
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
        user_connection: UserConnection, 
        message: str
    ):
        r = request(
            method='POST',
            url=f'http://{settings.API_URL}/api/v1/chat/{self.chat.pk}/messages/',
            data={"text": message},
            headers={
                'Authorization': f'Bearer {user_connection.user.token}'
            }
        )
        data = r.json()
        if r.status_code != 201:
            print(f'SOME ERROR! : {data=}')

        message = {
            'type': 'message',
            'content': data
        }

        for user_connection in self.users:
            await user_connection.websocket.send_json(message)

class ConnectionsManager:
    def __init__(self) -> None:
        self.chats: dict[int, Connection] = {}

    def get_chat_connection(self, chat: Chat) -> Connection:
        if chat.pk not in self.chats:
            self.chats[chat.pk] = Connection(chat)

        return self.chats[chat.pk]
        


