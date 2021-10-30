from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse

from settings import settings

from models import User, UserConnection, Membership, Chat
from managers import ConnectionsManager, Connection

from dependencies import authenticate, get_chat

app = FastAPI()

manager = ConnectionsManager()

print(f'http://{settings.API_URL}/api/v1/accounts/user/')


@app.get('/')
async def get():
    with open('index.html', 'r') as file:
        html = file.read()
    return HTMLResponse(html)

@app.get('/info/')
async def info():
    return settings.dict()


@app.websocket('/ws/{chat_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    chat: Chat = Depends(get_chat), 
    user: User = Depends(authenticate)
):
    await websocket.accept()

    if not (user and chat):
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
                    user_connection=user_connection, 
                    message=f'{user.username}: {data["content"]}'
                )
    except WebSocketDisconnect:
        await chat.disconnect(user_connection)



