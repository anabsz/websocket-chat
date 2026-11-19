
import asyncio
import json
import logging
from datetime import datetime, timezone

from websockets.asyncio.server import serve

HOST = "localhost"
PORT = 8765

connected_clients = {}


async def send_message(websocket, data):
    await websocket.send(json.dumps(data))


async def broadcast(data):
    clients = list(connected_clients)
    if not clients:
        return

    message = json.dumps(data)
    results = await asyncio.gather(*[client.send(message) for client in connected_clients], return_exceptions=True)

    for client, result in zip(clients, results):
        if isinstance(result, Exception):
            connected_clients.pop(client, None)


async def broadcast_users():
    await broadcast({
        "type": "users_update",
        "users": list(connected_clients.values())
    })


async def handle_client(websocket):
    client_address = websocket.remote_address
    username = None
    logging.info("Cliente conectado: %s", client_address)

    try:
        async for message in websocket:
            logging.info(
                "Mensagem recebida de %s: %s",
                client_address,
                message
            )

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await send_message(websocket, {
                    "type": "error",
                    "content": "Formato de mensagem inválido."
                })
                continue

            message_type = data.get("type")
            if message_type == "join":
                requested_username = data.get("username", "").strip()
                if not requested_username:
                    await send_message(websocket, {
                        "type": "error",
                        "content": "Nome de usuário inválido."
                    })
                    continue

                if username is not None:
                    continue
                username = requested_username[:30]
                connected_clients[websocket] = username
                logging.info("Usuário entrou: %s", username)

                await broadcast({
                    "type": "user_joined",
                    "username": username
                })

                await broadcast_users()

            elif message_type == "chat_message":
                if websocket not in connected_clients:
                    continue

                content = data.get("content", "").strip()

                if not content:
                    continue

                await broadcast({
                    "type": "chat_message",
                    "username": connected_clients[websocket],
                    "content": content[:1000],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

    except Exception:
        logging.exception("Erro na conexão %s", client_address)

    finally:
        disconnected_username = connected_clients.pop(websocket, None)

        if disconnected_username:
            logging.info("Usuário desconectado: %s", disconnected_username)
            await broadcast({
                "type": "user_left",
                "username": disconnected_username
            })
            await broadcast_users()

        logging.info("Conexão encerrada: %s", client_address)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    async with serve(handle_client, HOST, PORT):
        logging.info(
            "Servidor WebSocket iniciado em ws://%s:%s",
            HOST,
            PORT
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
