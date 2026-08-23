# 24PFD

A real-time, Airbus-style **Primary Flight Display** for the ATC24 / PTFS Roblox flight-simulator community. Run it on a second monitor beside the game and it renders a live instrument panel — attitude, airspeed, altitude, heading and vertical speed — for the aircraft you select.

> **What it is and isn't:** 24PFD is a focused instrument panel, not a flight-planning or ATC tool. Those features belong to sibling ATC24 tools such as `24Flight`. This project plans to grow into a multi-panel EFIS (PFD + Navigation Display + MCDU), but the current release is the PFD only.

## Features

- Airbus-authentic cockpit styling — gunmetal bezels, ECAM color coding, B612 / B612 Mono typography.
- Attitude indicator, speed tape, altitude tape, heading tape and vertical-speed indicator.
- GPWS-style audio callouts (altitude thresholds, "retard", plus a set of warning sounds).
- Per-instrument staleness flags and a full-panel failure banner when the relay connection drops.
- Day / Night cockpit-lighting toggle (not a generic light/dark theme).
- Automatic reconnect with exponential backoff on the upstream feed.

## How it works

```
ATC24/PTFS game
      │  (wss://ws.awdevhardware.org — community relay)
      ▼
main.py ─── derives pitch / roll / vertical speed from
      │     heading · altitude · groundSpeed deltas
      ▼
back_front_ws.py ─── local WebSocket relay on ws://localhost:8765
      │
      ▼
graphicsvg.html (browser) ─── renders the SVG PFD
```

The upstream feed provides only `heading`, `groundSpeed` and `altitude` — no real attitude telemetry. **Pitch and roll are derived client-side** from altitude / heading / speed deltas. This is an approximation, not real attitude data, and the project is deliberately honest about that: it will never fabricate ILS, glideslope or flight-director data the feed doesn't provide.

## Requirements

- **Python 3.11+** with `websockets==16.0` (see `24PFD/requirements.txt`).
- A modern browser (the frontend is a static HTML page, no build step).
- Node.js 22 is only needed to run the frontend test suite.

## Quick start

```bash
cd 24PFD
pip install -r requirements.txt
python main.py
```

Then open `24PFD/graphicsvg.html` in your browser. The panel starts on `ws://localhost:8765` and populates the aircraft dropdown from live traffic — pick your callsign and fly.

## Configuration

The backend reads its settings from environment variables (defined in `24PFD/config.py`):

| Variable | Default | Purpose |
|---|---|---|
| `PFD_UPSTREAM_WS_URI` | `wss://ws.awdevhardware.org` | Upstream feed to connect to |
| `PFD_RELAY_HOST` | `0.0.0.0` | Host the local relay binds to |
| `PFD_RELAY_PORT` | `8765` | Port the browser connects to |
| `PFD_UPDATE_RATE` | `1.0` | Seconds between processed upstream packets |
| `PFD_RECONNECT_DELAY_INITIAL` | `1.0` | First reconnect delay (seconds) |
| `PFD_RECONNECT_DELAY_MAX` | `30.0` | Reconnect delay ceiling (seconds) |
| `PFD_STABLE_CONNECTION_THRESHOLD` | `60.0` | Stable-connection time before backoff resets |

> The frontend currently connects to `ws://localhost:8765` hardcoded. Change it in `graphicsvg.html` if you run the relay elsewhere.

## Testing

Backend (pytest) and frontend (node:test + jsdom) suites run in CI on every push and PR.

```bash
cd 24PFD

# Backend
pip install -r requirements-dev.txt
python -m pytest

# Frontend
npm install
npm test
```

## Project structure

```
24PFD/
├── PRODUCT.md                  # Product definition and principles
├── .github/workflows/tests.yml # CI (pytest + node:test)
└── 24PFD/                      # The application
    ├── main.py                 # Upstream WS client + flight-dynamics derivation
    ├── back_front_ws.py        # Local relay WebSocket server
    ├── config.py               # Env-var configuration
    ├── graphicsvg.html         # The SVG PFD frontend
    ├── styles.css              # Cockpit / ECAM styling
    ├── sounds/                 # GPWS and warning audio assets
    ├── tests/                  # Backend pytest suite
    └── tests-js/               # Frontend node:test + jsdom suite
```

## Roadmap

- Navigation Display and MCDU as sibling panels in the same app.
- Flight-planning and ATC features stay **out of scope** — they belong to `24Flight` and the wider ATC24 tooling.

## License

No license is currently specified.
