import asyncio
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


def get_uuid() -> str:
    return str(uuid4())[:8]


class ConnectionManager:
    """Управляет подключениями клиентов"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, _id: str):
        """Добавляет нового клиента в список"""
        await websocket.accept()
        self.active_connections[_id] = websocket

    async def disconnect(self, _id: str):
        """Удаляет клиента из списка при отключении"""
        del self.active_connections[_id]
        await self.broadcast(_id, f'{_id} disconnected')

    async def broadcast(self, _id: str, message: str):
        """Отправляет сообщение всем подключённым клиентам"""
        for user_id, connection in self.active_connections.items():
            if user_id == _id:
                await connection.send_text(f'YOU: {message}')
            else:
                await connection.send_text(f'{_id}: {message}')\

    async def send_message(self, _id: str, message: str):
        """Отправляет сообщение конкретному клиенту"""
        if _id in self.active_connections:
            await self.active_connections[_id].send_text(message)
        else:
            print(f'Message to non-existent user: {_id}')


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Обрабатывает WebSocket-соединение"""
    _id = get_uuid()
    print(f'New connection: {_id}')
    await manager.connect(websocket, _id)
    await manager.broadcast(_id, 'connected')

    async def send_pings():
        """Проверяет соединение каждые 10 секунд."""
        while True:
            try:
                await websocket.send_text('ping')  # Отправляем ping клиенту
                await asyncio.sleep(10)  # Проверяем раз в 10 секунд
            except:
                print("🔴 Клиент отключился (нет ответа на Ping)")
                await manager.disconnect(_id)
                break

    asyncio.create_task(send_pings())  # Запускаем Ping в фоне

    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith('@'):
                potential_target = data.split()[0].replace('@', '')
                if potential_target in manager.active_connections:
                    await manager.send_message(potential_target, data.split(potential_target)[-1])  # Отправка сообщения конкретному клиенту
            else:
                await manager.broadcast(_id, data)  # Рассылка сообщения всем клиентам
    except WebSocketDisconnect:
        await manager.disconnect(_id)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                if (event.data === "ping") {
                    ws.send("pong");
                } else {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                }
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)
