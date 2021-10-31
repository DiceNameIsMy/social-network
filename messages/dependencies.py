from requests import request

from fastapi import Depends, HTTPException

from models import User, UserConnection, Chat
from utils import send_api_request


def get_user(token: str) -> User:
    r = send_api_request(
        method='GET',
        url=f'/api/v1/accounts/user/',
        user=User(token=token)
    )
    if r.status_code != 200:
        return User()
    
    return User(
        **r.json(), 
        token=token,
        is_authenticated=True
    )


def get_chat(chat_id: int, token: str, user: User = Depends(get_user)) -> Chat:
    r = send_api_request(
        method='GET',
        url=f'/api/v1/chats/{chat_id}/',
        user=user
    )
    if r.status_code != 200:
        return Chat()

    return Chat(**r.json(), is_valid=True)


def authenticate(user: User = Depends(get_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Token is invalid or expired'
        )
    
    return user
