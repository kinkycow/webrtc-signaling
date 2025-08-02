import asyncio
import json
import websockets
import http.server
import socketserver
import threading

ROOMS = {}  # room_id → list of websockets

# ========== HTTP SERVER FOR RENDER HEALTH CHECK ==========
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_error(404)

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_healthcheck():
    with socketserver.TCPServer(("", 80), HealthCheckHandler) as httpd:
        print("HTTP healthcheck server running on port 80")
        httpd.serve_forever()

# ========== WEBSOCKET RELAY SERVER ==========
async def ws_handler(ws, path):
    room = None
    try:
        async for msg in ws:
            obj = json.loads(msg)
            if "room" in obj:
                room = obj["room"]
                ROOMS.setdefault(room, []).append(ws)
            for peer in ROOMS.get(room, []):
                if peer != ws:
                    await peer.send(msg)
    except:
        pass
    finally:
        if room and ws in ROOMS.get(room, []):
            ROOMS[room].remove(ws)

async def run_ws():
    async with websockets.serve(ws_handler, "0.0.0.0", 443):
        print("WebSocket signaling server running on port 443")
        await asyncio.Future()

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    # Run HTTP healthcheck server on separate thread
    threading.Thread(target=run_http_healthcheck, daemon=True).start()

    # Run WebSocket server (async)
    asyncio.run(run_ws())
