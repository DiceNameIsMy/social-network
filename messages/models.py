from typing import Optional, DefaultDict

from fastapi import WebSocket

from pydantic import BaseModel


class User(BaseModel):
    pk: Optional[int] = None
    username: str = ''
    token: str = ''

    is_authenticated: bool = False


class Membership(BaseModel):
    pk: int
    type: int
    user: int


class Chat(BaseModel):
    pk: Optional[int] = None
    title: str = ''
    type: Optional[int]
    memberships: list[Membership] = []
    members_amount: Optional[int]

    is_valid: bool = False


class UserConnection(BaseModel):
    user: User
    chat: Chat
    websocket: WebSocket

    class Config:
        arbitrary_types_allowed = True

