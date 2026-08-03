import os

# Upstream feed this app connects to
WS_URI = os.environ.get("PFD_UPSTREAM_WS_URI", "wss://ws.awdevhardware.org")

# Local relay server that the browser frontend (graphicsvg.html) connects to
RELAY_HOST = os.environ.get("PFD_RELAY_HOST", "0.0.0.0")
RELAY_PORT = int(os.environ.get("PFD_RELAY_PORT", "8765"))

# How often incoming upstream packets are processed, in seconds
UPDATE_RATE = float(os.environ.get("PFD_UPDATE_RATE", "1.0"))

# Reconnect backoff for the upstream WebSocket connection
RECONNECT_DELAY_INITIAL = float(os.environ.get("PFD_RECONNECT_DELAY_INITIAL", "1.0"))
RECONNECT_DELAY_MAX = float(os.environ.get("PFD_RECONNECT_DELAY_MAX", "30.0"))
STABLE_CONNECTION_THRESHOLD = float(os.environ.get("PFD_STABLE_CONNECTION_THRESHOLD", "60.0"))
