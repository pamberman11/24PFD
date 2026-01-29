import websockets
import asyncio
import json
from main import pitch_angle_degrees
from main import roll_deg

acdata = {
    pitch_angle_degrees: 0.0,
    roll_deg: 0.0
}
async def handler(ws):
    print("Client connected")

    while True:
        await ws.send("hello")
        await ws.send(acdata)
        await asyncio.sleep(1)

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WS server running on port 8765")
    await server.wait_closed()

asyncio.run(main())