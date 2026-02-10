import websockets
import asyncio
import json
#from main import roll_deg
def update_acdataws(acdata):
    global acdataws
    acdataws = acdata
    

def set_pitch(pitch):
    global acdataws
    acdataws["pitch_angle_degrees"] = pitch
    print(f"Pitch set to: {pitch}")
    return pitch
    
def set_roll(roll):
    global acdataws
    roll_deg = roll
    acdataws["roll_deg"] = roll_deg
    print(f"Roll set to: {roll_deg}")
    return roll_deg


acdataws = {

    "pitch_angle_degrees": 0.0,
    "roll_deg": 0.0,
}
async def handler(ws):
    print("Client connected")

    while True:
        # await ws.send("hello")
        await ws.send(json.dumps(acdataws))
        await asyncio.sleep(1)

async def back_front():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WS server running on port 8765")
    await server.wait_closed()

