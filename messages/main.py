from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, logger
from fastapi.responses import HTMLResponse

from settings import settings

from models import User, Chat
from managers import ConnectionsManager, Connection

from dependencies import get_user, get_chat, authenticate

app = FastAPI()

manager = ConnectionsManager()


@app.get('/')
async def get():
    if settings.debug:
        with open('index.html', 'r') as file:
            html = file.read()
    else:
        with open('index.prod.html', 'r') as file:
            html = file.read()

    return HTMLResponse(html)

@app.get('/info/')
async def info():
    return settings.dict()


@app.websocket('/ws/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    user: User = Depends(get_user),
    chat: Chat = Depends(get_chat),
):
    await websocket.accept()

    # if user or chat wasn't acquired close the connection
    if not (user and chat):
        logger.logger.info(f'{user.is_authenticated=}, {chat.is_valid}')
        await websocket.close()
        return
    
    chat: Connection = manager.get_chat_connection(chat)
    user_connection = await chat.connect(
        user=user, 
        websocket=websocket
    )
    try:
        while True:
            data = await websocket.receive_json()
            if data['type'] == 'message':
                await chat.send_message(
                    user=user, 
                    message=f'{user.username}: {data["content"]}'
                )
    except WebSocketDisconnect:
        await chat.disconnect(user_connection)



