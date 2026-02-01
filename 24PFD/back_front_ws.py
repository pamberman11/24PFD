import websockets
import asyncio
import json
#from main import roll_deg

def set_pitch(pitch):
    global acdata
    acdata["pitch_angle_degrees"] = pitch
    print(f"Pitch set to: {pitch}")
    return pitch

def set_roll(roll):
    global roll_deg
    global acdata
    roll_deg = roll
    acdata["roll_deg"] = roll_deg
    print(f"Roll set to: {roll_deg}")
    return roll_deg


acdata = {
    "pitch_angle_degrees": 0.0,
    "roll_deg": 0.0,
    #"pitch_angle_degrees": 15.0,
    #"roll_deg": 10.0
}
async def handler(ws):
    print("Client connected")

    while True:
        # await ws.send("hello")
        await ws.send(json.dumps(acdata))
        await asyncio.sleep(1)

async def back_front():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WS server running on port 8765")
    await server.wait_closed()

