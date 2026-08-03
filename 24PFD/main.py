import websockets
import asyncio
import json
import time
import math
import logging
import back_front_ws # Import the back_front_ws module
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def remove_non_aircraft_entries(ACdata, content):

    active_callsigns = set()

    for callsign, aircraft in content.items():
        if isinstance(aircraft, dict):
            active_callsigns.add(callsign)

    for callsign in list(ACdata.keys()):
        if callsign not in active_callsigns:
            del ACdata[callsign]

def update_aircraftt(datatype, content, dt): #this funciton updates the aircraft data every second and also calculates pitch and roll angles
    #print (f"Updating aircraft {datatype} with data: {content}")
    if datatype == "d":
        global ACdata
        global callsign
        # The upstream feed reuses the "d" key for non-aircraft event types too (e.g. CONTROLLERS,
        # whose "d" payload is a Position[] list, not AircraftData) - only dict payloads are aircraft data.
        if not isinstance(content, dict):
            logger.debug("Skipping non-aircraft 'd' payload (type=%s)", type(content).__name__)
            return
        try:
            remove_non_aircraft_entries(ACdata, content)
            #print("Content received:", content)
            for callsign, aircraft in content.items(): #take data for each specific aircraft
                # Prevent non-aircraft dictionary entries (like "robloxName", "altitude") from being parsed as callsigns
                if type(aircraft) is not dict:
                    continue
                try:
                    if callsign in ACdata:
                        #print(f"Processing data for aircraft {callsign}")
                        #print(ACdata[callsign])
                        ACdata[callsign].update(prev_altitude = ACdata[callsign]['altitude']) #old values are saved
                        ACdata[callsign].update(prev_heading = ACdata[callsign]['heading'])
                        #ACdata[callsign].update(prev_time = ACdata[callsign]['time'])
                        #ACdata[callsign].update(time = time.time())
                        
                        ACdata[callsign].update(heading = aircraft['heading']) #New values are saved 
                        ACdata[callsign].update(groundSpeed = aircraft['groundSpeed'])
                        ACdata[callsign].update(altitude = aircraft['altitude'])  

                        #Devrided 
                        ACdata[callsign].update(vertical_speed_fps = vertical_speed_calculation(ACdata[callsign]['altitude'], ACdata[callsign]['prev_altitude'], dt))
                        ACdata[callsign].update(forward_speed_fps = forward_speed_fps_calculation(ACdata[callsign]['groundSpeed']))
                        ACdata[callsign].update(pitch = pitch_angle_calculation(ACdata[callsign]['vertical_speed_fps'], ACdata[callsign]['forward_speed_fps']))
                        ACdata[callsign].update(roll = bank_angle(
                        ACdata[callsign]['heading'], ACdata[callsign]['prev_heading'], dt, ACdata[callsign]['forward_speed_fps'] / 1.8372 / 0.5442765  # back to studs/s
                ))
                    else:
                        ACdata[callsign] = new_aircraft_state()
                except Exception:
                    logger.exception("Error processing aircraft data for %s", callsign)
        except Exception:
            logger.exception("Error updating aircraft data")

    
def new_aircraft_state():
    return {
        "altitude": 0,
        "heading": 0,
        "groundSpeed": 0,

        "prev_altitude": 0,
        "prev_heading": 0,
        "prev_time": time.time(),

        "forward_speed_fps": 0,
        "vertical_speed_fps": 0,
        "pitch": 0,
        "roll": 0
    }

ACdata = {}
dt = 1.0  # Initial delta time

def vertical_speed_calculation(altitude, oldaltitude, dt):  # Calculate vertical speed in feet per second
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
    #back_front_ws.set_pitch(pitch_deg)
    # print(f"Pitch Angle: {pitch_deg} degrees")
    return pitch_deg

def bank_angle(heading, oldheading, dt, speed_studs_s):
    delta_heading = ((heading - oldheading + 180) % 360) - 180
    turn_rate_rad_s = math.radians(delta_heading / dt)
    speed_m_s = speed_studs_s * 0.28
    roll_rad = math.atan((turn_rate_rad_s * speed_m_s) / 9.81)
    return math.degrees(roll_rad)

async def listen():     # Listen for incoming WebSocket messages, reconnecting with backoff on failure
    delay = config.RECONNECT_DELAY_INITIAL
    while True:
        connected_at = None
        try:
            logger.info("Connecting to WebSocket server...")
            async with websockets.connect(config.WS_URI) as ws:
                logger.info("Connected to WebSocket server")
                connected_at = time.time()
                async for message in ws:
                    handle_packet(message)
        except (websockets.exceptions.ConnectionClosed, OSError, asyncio.TimeoutError) as e:
            logger.warning("WebSocket connection lost: %s", e)
        except Exception:
            logger.exception("Unexpected error in WebSocket listener")

        if connected_at is not None and time.time() - connected_at >= config.STABLE_CONNECTION_THRESHOLD:
            delay = config.RECONNECT_DELAY_INITIAL
        else:
            delay = min(delay * 2, config.RECONNECT_DELAY_MAX)

        logger.info("Reconnecting in %.1f seconds...", delay)
        await asyncio.sleep(delay)

last_update_time = 0

def handle_packet(raw):
    global last_update_time
    now = time.time()
    real_dt = now - last_update_time
    if real_dt < config.UPDATE_RATE:
        return
    last_update_time = now
    data = json.loads(raw)
    for datatype, content in data.items():
        update_aircraftt(datatype, content, real_dt)  # ← pass actual elapsed time
        back_front_ws.update_acdataws(ACdata)
            
async def main():
        await asyncio.gather(listen(), back_front_ws.back_front())


logger.info("Starting WebSocket listener...")
asyncio.run(main())