
import asyncio
import threading

from app import create_app
from app.websocket_server import main as websocket_main


def start_websocket_server():
    asyncio.run(websocket_main())


if __name__ == "__main__":
    websocket_thread = threading.Thread(
        target=start_websocket_server,
        daemon=True
    )

    websocket_thread.start()

    app = create_app()

    app.run(
        host="localhost",
        port=5000,
        debug=False,
        use_reloader=False
    )
