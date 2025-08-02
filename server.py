import asyncio, json
import websockets
from http import HTTPStatus

ROOMS = {}  # room_id → active websocket list

async def process_request(path, request_headers):
    if path == "/healthz":
        # Return HTTP 200 without upgrading to WebSocket
        return HTTPStatus.OK, [], b"OK"
    return None  # treat other paths as WebSocket handshake

async def ws_handler(ws, path):
    room = None
    try:
        async for msg in ws:
            obj = json.loads(msg)
            if "room" in obj:
                room = obj["room"]
                ROOMS.setdefault(room, []).append(ws)
            # broadcast to others in same room
            for peer in ROOMS.get(room, []):
                if peer != ws:
                    await peer.send(msg)
    except websockets.ConnectionClosed:
        pass
    finally:
        if room and ws in ROOMS.get(room, []):
            ROOMS[room].remove(ws)

async def main():
    port = 443
    async with websockets.serve(
        ws_handler, "0.0.0.0", port, process_request=process_request
    ):
        print(f"WebSocket signaling + health check running on port {port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
