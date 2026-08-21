"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

test("renderLoop interpolates smoothState toward aircraftState by the fixed factor", () => {
  const w = loadPage();
  w.eval(`
    aircraftState.pitch = 10;
    smoothState.pitch = 0;
  `);
  w.renderLoop();
  const pitch = w.eval("smoothState.pitch");
  // factor = 0.1 -> exactly 1.0 after one tick
  assert.ok(Math.abs(pitch - 1.0) < 1e-9, `expected ~1.0, got ${pitch}`);
});

test("renderLoop heading interpolation takes the short way across the 0/360 wrap", () => {
  const w = loadPage();
  w.eval(`
    aircraftState.heading = 350;
    smoothState.heading = 10;
  `);
  w.renderLoop();
  const heading = w.eval("smoothState.heading");
  // Going from 10 toward 350 the short way is DOWN through 0/360 (10 -> 0 -> 350),
  // so smoothState.heading should decrease (wrap to just under 360), not increase toward 350 the long way.
  assert.ok(heading > 350 || heading < 10, `expected short-way wrap, got ${heading}`);
});

test("renderLoop keeps smoothState.heading normalized within [0, 360)", () => {
  const w = loadPage();
  w.eval(`
    aircraftState.heading = 5;
    smoothState.heading = 355;
  `);
  for (let i = 0; i < 50; i++) w.renderLoop();
  const heading = w.eval("smoothState.heading");
  assert.ok(heading >= 0 && heading < 360, `heading out of range: ${heading}`);
});

test("renderLoop converges smoothState to aircraftState after many ticks", () => {
  const w = loadPage();
  w.eval(`
    aircraftState.altitude = 4500;
    aircraftState.groundSpeed = 220;
    aircraftState.ias = 210;
    smoothState.altitude = 0;
    smoothState.groundSpeed = 0;
    smoothState.ias = 0;
  `);
  for (let i = 0; i < 200; i++) w.renderLoop();
  assert.ok(Math.abs(w.eval("smoothState.altitude") - 4500) < 1, "altitude did not converge");
  assert.ok(Math.abs(w.eval("smoothState.ias") - 210) < 1, "ias did not converge");
});
