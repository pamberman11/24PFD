"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

function sendMessage(w, payload) {
  w.eval(`ws.onmessage(${JSON.stringify({ data: JSON.stringify(payload) })})`);
}

test("ws.onmessage populates the callsign dropdown for likely-callsign aircraft entries", () => {
  const w = loadPage();
  sendMessage(w, {
    "TEST-123": { altitude: 1000, heading: 90, groundSpeed: 200, ias: 190 },
  });
  const options = Array.from(w.document.querySelectorAll("#callsignSelect option")).map((o) => o.value);
  assert.ok(options.includes("TEST-123"));
});

test("ws.onmessage ignores keys that don't look like callsigns (no dash) or lack an altitude field", () => {
  const w = loadPage();
  sendMessage(w, {
    robloxName: "someplayer",
    pitch_angle_degrees: 0,
    "TEST-1": { altitude: 1000, heading: 1, groundSpeed: 1 },
  });
  const options = Array.from(w.document.querySelectorAll("#callsignSelect option")).map((o) => o.value);
  assert.ok(!options.includes("robloxName"));
  assert.ok(options.includes("TEST-1"));
});

test("ws.onmessage does not add duplicate dropdown options for an already-known callsign", () => {
  const w = loadPage();
  sendMessage(w, { "TEST-1": { altitude: 1000, heading: 1, groundSpeed: 1 } });
  sendMessage(w, { "TEST-1": { altitude: 1200, heading: 5, groundSpeed: 1 } });
  const options = Array.from(w.document.querySelectorAll("#callsignSelect option")).filter((o) => o.value === "TEST-1");
  assert.equal(options.length, 1);
});

test("ws.onmessage updates aircraftState only for the currently active callsign", () => {
  const w = loadPage();
  w.eval(`activeCallsign = "TEST-1"; lastActiveDataTime = null;`);
  sendMessage(w, {
    "TEST-1": { altitude: 1000, heading: 90, groundSpeed: 200, ias: 180, roll: 12, pitch: -3, vertical_speed_fps: 5 },
    "TEST-2": { altitude: 2000, heading: 45, groundSpeed: 100, ias: 90 },
  });
  const state = w.eval("aircraftState");
  assert.equal(state.altitude, 1000);
  assert.equal(state.heading, 90);
  assert.equal(state.roll, 12);
  assert.equal(state.pitch, -3);
  // Backend sends vertical speed in ft/s, frontend converts to ft/min (*60)
  assert.equal(state.verticalSpeed, 300);
});

test("ws.onmessage is a no-op for aircraftState when no callsign is selected", () => {
  const w = loadPage();
  w.eval(`activeCallsign = null;`);
  const before = w.eval("JSON.stringify(aircraftState)");
  sendMessage(w, { "TEST-1": { altitude: 9999, heading: 9, groundSpeed: 9 } });
  const after = w.eval("JSON.stringify(aircraftState)");
  assert.equal(before, after);
});

test("ws.onmessage is a no-op when the active callsign is absent from this frame", () => {
  const w = loadPage();
  w.eval(`activeCallsign = "MISSING-1";`);
  const before = w.eval("JSON.stringify(aircraftState)");
  sendMessage(w, { "TEST-1": { altitude: 9999, heading: 9, groundSpeed: 9 } });
  const after = w.eval("JSON.stringify(aircraftState)");
  assert.equal(before, after);
});

test("ws.onopen sets wsConnected true; ws.onclose sets it false", () => {
  const w = loadPage();
  w.eval("ws.onopen()");
  assert.equal(w.eval("wsConnected"), true);
  w.eval("ws.onclose()");
  assert.equal(w.eval("wsConnected"), false);
});
