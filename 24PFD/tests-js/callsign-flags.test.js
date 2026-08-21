"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

test("setCallsign resets smoothState, GPWS memory, and retard flag", () => {
  const w = loadPage();
  w.eval(`
    smoothState.pitch = 10; smoothState.roll = 20; smoothState.altitude = 5000;
    smoothState.groundSpeed = 200; smoothState.verticalSpeed = -500;
    gpwsMemory[500] = true; retardPlayed = true;
    const select = document.getElementById("callsignSelect");
    const opt = document.createElement("option");
    opt.value = "TEST-1"; opt.textContent = "TEST-1";
    select.appendChild(opt);
    select.value = "TEST-1";
  `);
  w.setCallsign();
  const smooth = w.eval("smoothState");
  assert.equal(smooth.pitch, 0);
  assert.equal(smooth.roll, 0);
  assert.equal(smooth.altitude, 0);
  assert.equal(smooth.groundSpeed, 0);
  assert.equal(smooth.verticalSpeed, 0);
  assert.equal(w.eval("gpwsMemory[500]"), false);
  assert.equal(w.eval("retardPlayed"), false);
  assert.equal(w.eval("activeCallsign"), "TEST-1");
});

test("setCallsign with empty selection clears activeCallsign and lastActiveDataTime", () => {
  const w = loadPage();
  w.eval(`document.getElementById("callsignSelect").value = ""`);
  w.setCallsign();
  assert.equal(w.eval("activeCallsign"), "");
  assert.equal(w.eval("lastActiveDataTime"), null);
});

test("updateFailFlags shows the PFD FAIL banner and hides other flags when wsConnected is false", () => {
  const w = loadPage();
  w.eval("wsConnected = false;");
  w.updateFailFlags();
  assert.equal(w.document.getElementById("pfd_fail_banner").style.display, "block");
  assert.equal(w.document.getElementById("flag_att").style.display, "none");
});

test("updateFailFlags shows SELECT AIRCRAFT prompt when connected but nothing selected", () => {
  const w = loadPage();
  w.eval("wsConnected = true; activeCallsign = null;");
  w.updateFailFlags();
  assert.equal(w.document.getElementById("pfd_fail_banner").style.display, "none");
  assert.equal(w.document.getElementById("no_aircraft_prompt").style.display, "block");
});

test("updateFailFlags raises per-instrument fail flags once data goes stale", () => {
  const w = loadPage();
  w.eval(`
    wsConnected = true;
    activeCallsign = "TEST-1";
    lastActiveDataTime = Date.now() - 10000; // 10s ago, way past STALE_DATA_MS (3000)
  `);
  w.updateFailFlags();
  assert.equal(w.document.getElementById("flag_att").style.display, "block");
  assert.equal(w.document.getElementById("flag_hdg").style.display, "block");
});

test("updateFailFlags does not raise fail flags for freshly-arriving data", () => {
  const w = loadPage();
  w.eval(`
    wsConnected = true;
    activeCallsign = "TEST-1";
    lastActiveDataTime = Date.now();
  `);
  w.updateFailFlags();
  assert.equal(w.document.getElementById("flag_att").style.display, "none");
});
