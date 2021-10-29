from requests import request

from settings import settings

from models import User, UserConnection, Chat


def authenticate(token: str) -> User:
    r = request(
        method='GET',
        url=f'http://{settings.API_URL}/api/v1/accounts/user/',
        headers={'Authorization': f'Bearer {token}'}
    )
    if r.status_code != 200:
        return User()
    
    return User(
        **r.json(), 
        token=token,
        is_authenticated=True
    )


def get_chat(chat_id: int, token: str) -> Chat:
    r = request(
        method='GET',
        url=f'http://{settings.API_URL}/api/v1/chat/{chat_id}/',
        headers={'Authorization': f'Bearer {token}'},
    )
    if r.status_code != 200:
        return Chat()

    return Chat(**r.json(), is_valid=True)

