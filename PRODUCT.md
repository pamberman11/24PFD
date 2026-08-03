# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

PTFS/ATC24 pilots (Roblox flight-sim community), using 24PFD as a personal cockpit
companion on a second monitor while actively flying. Single local user per running
instance — no accounts, no audience, no shared/spectator viewing.

## Product Purpose

A real-time, Airbus-style Primary Flight Display that visualizes live flight telemetry
(pitch, roll, altitude, airspeed, heading, vertical speed) for a selected aircraft in the
ATC24/PTFS Roblox flight simulator, giving pilots an authentic-feeling instrument panel
to run beside the game window. Currently the first panel of a planned multi-instrument
EFIS suite — a Navigation Display and MCDU are planned as sibling panels in this same
app (confirmed 2026-08-03; see backlog reference below).

## Positioning

Distinct from `24Flight` (the ATC24 community's full pilot/controller client suite,
covering flight plans, ATC comms, and more) by staying a focused instrument-panel
experience rather than a flight-planning or control tool. Its mechanism: connect to the
community relay feed (`wss://ws.awdevhardware.org`, itself relaying 24data), derive flight
dynamics client-side since the source provides no real attitude data, and render an
authentic cockpit-style panel — growing into a multi-panel EFIS (PFD + ND + MCDU) while
flight-planning/ATC features stay out of scope and belong to sibling ATC24 tools.

## Operating Context

Run locally: the user starts `python main.py` (connects to the upstream relay, computes
derived flight dynamics, and also launches the local `back_front_ws` relay server via
`asyncio.gather`), then opens `graphicsvg.html` in a browser. They select their aircraft's
callsign from a dropdown that populates live from incoming traffic, and watch the
instrument update in real time. No login, no multi-user session; one local user, one
active aircraft at a time.

## Capabilities and Constraints

- Upstream feed provides `heading`, `groundSpeed` (Roblox "knots", needs unit conversion),
  and `altitude` only — no real pitch/roll/attitude data, no ILS/localizer/glideslope, no
  autopilot target or armed-mode data.
- Pitch and roll are **derived client-side** from altitude/heading/speed deltas
  (`update_aircraftt` in `main.py`) — an approximation, not real attitude telemetry.
- Confirmed non-goals (decided 2026-08-03): no ILS/localizer/glideslope and no flight
  director/FMA in the current PFD panel — both would require fabricating data the feed
  doesn't provide, which conflicts with the authenticity principle below.
- Implemented: attitude indicator, speed/altitude/heading tapes, vertical speed indicator,
  per-instrument failure/staleness flags (stale-data flags per tape, a full-panel failure
  banner when the relay connection itself drops), GPWS-style audio callouts.
- Backend has WS reconnect/backoff and structured logging; URLs/ports/rates are
  environment-variable driven via `config.py`.
- Planned: MCDU and Navigation Display as additional panels within this same app (per
  backlog board and 2026-08-03 confirmation) — not yet built.

## Brand Commitments

- Name "24PFD" follows the shared "24" naming convention across ATC24 community tools
  (`24Flight`, `24tab`, `24Route`/`rufusz`).
- Visual identity (established 2026-08-03): Airbus-authentic cockpit styling — gunmetal
  bezels, ECAM-standard color coding (white/green/cyan/amber/red/magenta), B612/B612 Mono
  typography (Airbus's real cockpit typeface). This replaced an earlier generic
  "editorial portfolio" pass that the user explicitly rejected as wrong for this product.
- A Day/Night cockpit-lighting toggle (not a generic light/dark theme) is a deliberate
  identity choice, not a default web pattern.
- The instrument face's functional aviation colors (cyan pointers, amber/red fail flags,
  sky/ground attitude colors) are fixed by convention and not subject to theme/lighting
  changes — only the surrounding bezel and chrome dim for night lighting.

## Evidence on Hand

- GitHub Projects backlog: `github.com/users/pamberman11/projects/1` ("@24PFD" project) —
  tracks Planned (MCDU, Navigation Display), Todo, and Done items. As of 2026-08-03 some
  Todo items (airspeed/altimeter tape, heading indicator) were already shipped in code but
  not marked Done on the board — treat the board as directionally useful, not literally
  accurate against current code state.
- 24data API reference at `../24data API.txt` (parent ATC24 directory) documents the true
  upstream schema; 24PFD connects through a third-party relay that forwards the same
  `{t, d, s}`-shaped messages rather than connecting to 24data directly.

## Product Principles

1. **Authenticity within honesty** — recreate Airbus cockpit look and color conventions
   faithfully, but never fabricate telemetry (ILS, autopilot/FD) the upstream feed doesn't
   actually provide.
2. **Single-user, low-ceremony companion** — no accounts or multi-client sharing; runs
   locally beside the game like a second-monitor gadget, not a hosted service.
3. **Grows as a cockpit suite, not a swiss-army tool** — new panels (ND, MCDU) extend the
   same instrument-panel experience; flight-planning and ATC features stay out of scope
   and belong to sibling ATC24 tools like `24Flight`.
4. **Resilience over cleverness** — prefer graceful degradation (reconnect/backoff,
   failure flags, skipping malformed payloads) over crashing or silently swallowing
   errors, since it runs unattended beside a live flight.
