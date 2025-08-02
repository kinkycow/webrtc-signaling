import asyncio, json
import websockets

ROOMS = {}  # room_id → list of websockets

async def handler(ws, path):
    room = None
    try:
        async for msg in ws:
            obj = json.loads(msg)
            if "room" in obj:
                room = obj["room"]
                ROOMS.setdefault(room, []).append(ws)
            # forward to peers in that room
            for peer in ROOMS.get(room, []):
                if peer != ws:
                    await peer.send(msg)
    except:
        pass
    finally:
        if room and ws in ROOMS.get(room, []):
            ROOMS[room].remove(ws)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 443):
        print("Signaling server listening on port 443")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
