from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    """Управляет подключениями клиентов"""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Добавляет нового клиента в список"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Удаляет клиента из списка при отключении"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Отправляет сообщение всем подключённым клиентам"""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Обрабатывает WebSocket-соединение"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)  # Рассылка сообщения всем клиентам
    except WebSocketDisconnect:
        manager.disconnect(websocket)
