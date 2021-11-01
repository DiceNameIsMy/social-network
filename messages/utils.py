from typing import Optional

from requests import request
from requests.models import Response

from models import User

from settings import settings


def send_api_request(
    method: str, 
    url: str, 
    user: Optional[User], 
    **kwargs
) -> Response:
    headers = {}
    if user is not None:
        headers['Authorization'] = f'Bearer {user.token}'

    return request(
        method=method,
        url=f'http://{settings.API_URL}{url}',
        headers=headers,
        **kwargs
    )