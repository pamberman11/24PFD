"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

test("update() rolls the attitude group opposite the sign of roll (right bank -> counter-clockwise)", () => {
  const w = loadPage();
  w.eval("smoothState.roll = 20; smoothState.pitch = 0;");
  w.update();
  const transform = w.document.getElementById("attitude").getAttribute("transform");
  // Positive roll must produce a NEGATIVE rotate() angle - this is the roll-invert fix.
  assert.match(transform, /rotate\(-20\)/);
});

test("update() with negative (left) roll produces a positive rotate angle", () => {
  const w = loadPage();
  w.eval("smoothState.roll = -15; smoothState.pitch = 0;");
  w.update();
  const transform = w.document.getElementById("attitude").getAttribute("transform");
  assert.match(transform, /rotate\(15\)/);
});

test("update() with zero roll produces rotate(0) / rotate(-0)", () => {
  const w = loadPage();
  w.eval("smoothState.roll = 0; smoothState.pitch = 0;");
  w.update();
  const transform = w.document.getElementById("attitude").getAttribute("transform");
  assert.match(transform, /rotate\(-?0\)/);
});

test("update() translates the attitude group vertically by pitch * PX_PER_DEG", () => {
  const w = loadPage();
  w.eval("smoothState.roll = 0; smoothState.pitch = 10; PX_PER_DEG = 5;");
  w.update();
  const transform = w.document.getElementById("attitude").getAttribute("transform");
  assert.match(transform, /translate\(0, 50\)/);
});

test("update() renders the IAS value (not groundspeed) on the speed tape text", () => {
  const w = loadPage();
  w.eval("smoothState.groundSpeed = 250; smoothState.ias = 180;");
  w.update();
  const text = w.document.getElementById("speed_text").textContent;
  assert.equal(text, "180");
});

test("update() renders altitude and heading text correctly", () => {
  const w = loadPage();
  w.eval("smoothState.altitude = 3456.7; smoothState.heading = 271.2;");
  w.update();
  assert.equal(w.document.getElementById("alt_text").textContent, "3457");
  assert.equal(w.document.getElementById("hdg_text").textContent, "271");
});

test("update() normalizes heading 360 to display as 000", () => {
  const w = loadPage();
  w.eval("smoothState.heading = 360;");
  w.update();
  assert.equal(w.document.getElementById("hdg_text").textContent, "000");
});

test("update() renders vertical speed rounded to nearest 50 with a leading + for climbs", () => {
  const w = loadPage();
  w.eval("smoothState.verticalSpeed = 733;");
  w.update();
  assert.equal(w.document.getElementById("vsi_text").textContent, "+750");
});

test("update() renders descending vertical speed without a + sign", () => {
  const w = loadPage();
  w.eval("smoothState.verticalSpeed = -733;");
  w.update();
  assert.equal(w.document.getElementById("vsi_text").textContent, "-750");
});
