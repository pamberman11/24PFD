from email.mime import message
import websockets
import asyncio
URI = "wss://24data.ptfs.app/wss"
import json
import time
import math
import back_front_ws # Import the back_front_ws module

def pitchmatch(oldaltitude, altitude, dt):
    vertical_speed = (altitude - oldaltitude) / dt  # feet per second
    pitch_angle = vertical_speed / (ACdata['groundSpeed'] * 1.68781)  # Convert groundspeed from knots to feet per second
    pitch_angle_degrees = pitch_angle * (180 / 3.14159)  # Convert radians to degrees
    return pitch_angle_degrees

def update_aircraftt(datatype, content): #denna funktion uppdaterar aircraft data varje sekund
    if datatype == "d":
        try:
            for callsign, aircraft in content.items(): #Tar datan från varje specifikt flygplan
                if callsign in ACdata:
                    print(f"Processing data for aircraft {callsign}")
                    print(ACdata[callsign])
                else:
                    ACdata[callsign] = new_aircraft_state()
        except Exception as e:
            print(f"Error processing aircraft data: {e}")

def new_aircraft_state():
    return {
        "altitude": 0,
        "heading": 0,
        "groundSpeed": 0,

        "prev_altitude": 0,
        "prev_heading": 0,
        "prev_time": time.time(),

        "pitch": 0,
        "roll": 0
    }

testcallsign = "Havoc-6283"
ACdata = {
    "null": None,
}
dt = 1.0  # Initial delta time

def vertical_speed_calculation(altitude, oldaltitude, dt):  # Beräknar vertikal hastighet i fots per sekund
    vertical_speed_fps = (
        altitude - oldaltitude
        ) / dt
    # print(f"Vertical Speed: {vertical_speed_fps} feet per second")
    return vertical_speed_fps

def forward_speed_fps_calculation(groundSpeed): 
    global groundspeed_studs_s 
    groundspeed_studs_s = groundSpeed * 0.5442765
    forward_speed_fps = groundspeed_studs_s * 1.8372
    # print(f"Forward Speed: {forward_speed_fps} feet per second")
    return forward_speed_fps

def pitch_angle_calculation(vertical_speed_fps, forward_speed_fps):
    
    pitch_rad = math.atan2(vertical_speed_fps, forward_speed_fps)
    pitch_deg = math.degrees(pitch_rad)
    back_front_ws.set_pitch(pitch_deg)
    # print(f"Pitch Angle: {pitch_deg} degrees")

def bank_angle(heading, oldheading, dt):
    delta_heading = (
    (ACdata["heading"] - ACdata["oldheading"] + 180) % 360
    ) - 180
    turn_rate_deg_s = delta_heading / dt
    turn_rate_rad_s = math.radians(turn_rate_deg_s)
    speed_m_s = groundspeed_studs_s * 0.28

    g = 9.81
    roll_rad = math.atan((turn_rate_rad_s * speed_m_s) / g)
    roll_deg = math.degrees(roll_rad)
    # print(f"Roll Angle: {roll_deg} degrees")
    back_front_ws.set_roll(roll_deg)
    return roll_deg

async def listen():     # Listen for incoming WebSocket messages
    print("Connecting to WebSocket server...")
    async with websockets.connect(URI) as ws:
        print("Connected to WebSocket server")
        async for message in ws:
            #print(message)
            handle_packet(message)
            
                
            #vertical_speed_calculation(ACdata['altitude'], ACdata['oldaltitude'], dt)
            #forward_speed_fps_calculation(ACdata['groundSpeed'])
            #pitch_angle_calculation(
                #vertical_speed_calculation(ACdata['altitude'], ACdata['oldaltitude'], dt),
                #forward_speed_fps_calculation(ACdata['groundSpeed'])
            #)
            #bank_angle(ACdata['heading'], ACdata['oldheading'], dt)

def handle_packet(raw):   # Process incoming WebSocket message
    data = json.loads(raw)
    for datatype, content in data.items():
        update_aircraftt(datatype, content=content)
    #for datatype, content in data.items():
        #update_aircraft(datatype, content)
                    

def update_aircraft(datatype, content): #denna funktion uppdaterar aircraft data varje sekund 
    #print (f"Updating aircraft {datatype} with data: {content}")
    if datatype == "d":
        try:
            for callsign, aircraft in content.items(): #Tar datan från varje specifikt flygplan
                if callsign == testcallsign:
                    print(f"Processing data for aircraft {callsign}")
                    print(aircraft['aircraftType'])
                    print(aircraft['altitude'])
                    print(aircraft['groundSpeed'])
                    print(aircraft['heading'])
                    print(aircraft['position']['y'])
                    print(aircraft['position']['x'])
                    #print(aircraft['callsign'])

                    #testACdata["oldtime"] = testACdata["time"]
                    ACdata["time"] = time.time()

                    ACdata.update(oldaltitude = ACdata['altitude']) #Gamla värden sparas
                    ACdata.update(oldgroundSpeed = ACdata['groundSpeed'])
                    ACdata.update(oldheading = ACdata['heading'])
                    ACdata.update(oldlatitude = ACdata['latitude'])
                    ACdata.update(oldlongitude = ACdata['longitude'])
                    ACdata.update(oldcallsign = ACdata['callsign'])

                    ACdata.update(altitude = aircraft['altitude'])  #Nya värden sparas
                    ACdata.update(groundSpeed = aircraft['groundSpeed'])
                    ACdata.update(heading = aircraft['heading'])
                    ACdata.update(latitude = aircraft['position']['y'])
                    ACdata.update(longitude = aircraft['position']['x'])
                    #ACdata.update(callsign = aircraft['callsign'])
                    global dt
                    dt = 1

                    return dt
        except Exception as e:
            print(f"Error processing aircraft data: {e}")
            return dt
            
async def main():
        await asyncio.gather(listen(), back_front_ws.back_front())


print("Starting WebSocket listener...")
#asyncio.run(listen())
asyncio.run(main())