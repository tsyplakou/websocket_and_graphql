import asyncio
import websockets

async def chat_client():
    uri = "ws://localhost:8000/ws"  # Адрес WebSocket-сервера
    async with websockets.connect(uri) as websocket:
        print("✅ Подключено к чату! Введите сообщение:")

        async def receive_messages():
            """Получает и отображает сообщения от сервера"""
            while True:
                try:
                    message = await websocket.recv()
                    print(f"\n💬 Новое сообщение: {message}")
                except websockets.exceptions.ConnectionClosed:
                    print("🔴 Соединение закрыто")
                    break

        async def send_messages():
            """Отправляет сообщения на сервер"""
            while True:
                message = input("Вы: ")
                if message.lower() in ["exit", "quit"]:
                    print("🔴 Отключаемся от чата...")
                    break
                await websocket.send(message)

        # Запускаем параллельно отправку и приём сообщений
        await asyncio.gather(receive_messages(), send_messages())

# Запуск клиента
if __name__ == "__main__":
    asyncio.run(chat_client())
