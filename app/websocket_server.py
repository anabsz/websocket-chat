import asyncio
import json
import logging
from datetime import datetime, timezone

from websockets.asyncio.server import serve

HOST = "localhost"
PORT = 8765

connected_clients = set()


async def broadcast(message):
    if not connected_clients:
        return

    disconnected_clients = set()

    for client in connected_clients.copy():
        try:
            await client.send(message)
        except Exception:
            disconnected_clients.add(client)

    connected_clients.difference_update(disconnected_clients)


async def handle_client(websocket):
    connected_clients.add(websocket)
    client_address = websocket.remote_address
    logging.info("Cliente conectado: %s", client_address)

    try:
        async for message in websocket:
            logging.info("Mensagem recebida de %s: %s", client_address, message)

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": "Formato de mensagem inválido."
                }))
                continue

            if data.get("type") == "chat_message":
                response = {
                    "type": "chat_message",
                    "username": data.get("username", "Anônimo"),
                    "content": data.get("content", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                await broadcast(json.dumps(response))

    except Exception as error:
        logging.error("Erro na conexão %s: %s", client_address, error)

    finally:
        connected_clients.discard(websocket)
        logging.info("Cliente desconectado: %s", client_address)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    async with serve(handle_client, HOST, PORT):
        logging.info("Servidor WebSocket iniciado em ws://%s:%s", HOST, PORT)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
