import websockets
import asyncio
import json
import config


def update_acdataws(acdata):
    global acdataws
    acdataws = acdata


acdataws = {

    "pitch_angle_degrees": 0.0,
    "roll_deg": 0.0,
}
async def handler(ws):
    print("Client connected")
    try:
        while True:
            await ws.send(json.dumps(acdataws))
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def back_front():
    server = await websockets.serve(handler, config.RELAY_HOST, config.RELAY_PORT)
    print(f"WS server running on port {config.RELAY_PORT}")
    await server.wait_closed()

