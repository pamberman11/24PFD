"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

test("checkGPWS does nothing on the very first call (seeds prevSmoothAlt, no crash)", () => {
  const w = loadPage();
  assert.doesNotThrow(() => w.checkGPWS(1500, -8));
});

test("checkGPWS fires a callout when crossing a threshold while descending steeply", () => {
  const w = loadPage();
  const played = [];
  w.eval("playSound = (f) => {}"); // will be overridden below via direct assignment
  w.playSound = (f) => played.push(f);
  w.checkGPWS(600, -8); // seed
  w.checkGPWS(490, -8); // crosses 500ft threshold while pitched down and descending fast enough
  assert.ok(played.includes("500.wav"), `expected 500.wav callout, got ${JSON.stringify(played)}`);
});

test("checkGPWS does not fire when pitch is shallow (not descending steeply)", () => {
  const w = loadPage();
  const played = [];
  w.playSound = (f) => played.push(f);
  w.checkGPWS(600, 0); // seed, level flight
  w.checkGPWS(490, 0); // crosses 500ft but pitch > -5, should not trigger GPWS logic at all
  assert.equal(played.length, 0);
});

test("checkGPWS does not re-fire the same threshold twice without climbing back above 2600", () => {
  const w = loadPage();
  const played = [];
  w.playSound = (f) => played.push(f);
  w.checkGPWS(600, -8);
  w.checkGPWS(490, -8);
  w.checkGPWS(480, -8); // still under 500, same descent - must not double-fire 500.wav
  const count500 = played.filter((f) => f === "500.wav").length;
  assert.equal(count500, 1);
});

test("checkGPWS memory resets once altitude climbs back above 2600ft", () => {
  const w = loadPage();
  const played = [];
  w.playSound = (f) => played.push(f);
  w.checkGPWS(600, -8);
  w.checkGPWS(490, -8); // fires 500.wav once
  w.checkGPWS(2700, -8); // climb above 2600 - resets gpwsMemory
  w.checkGPWS(2600, -8);
  w.checkGPWS(600, -8); // gradual re-descent (small enough deltas to not be treated as a teleport)
  w.checkGPWS(490, -8); // should be able to fire 500.wav again after reset
  const count500 = played.filter((f) => f === "500.wav").length;
  assert.equal(count500, 2);
});

test("checkGPWS fires retard.mp3 once between 5 and 25 ft while descending", () => {
  const w = loadPage();
  const played = [];
  w.playSound = (f) => played.push(f);
  w.checkGPWS(100, -8);
  w.checkGPWS(20, -8);
  assert.ok(played.includes("retard.mp3"));
  const retardCount = played.filter((f) => f === "retard.mp3").length;
  w.checkGPWS(15, -8);
  assert.equal(played.filter((f) => f === "retard.mp3").length, retardCount, "retard.mp3 must only play once per approach");
});

test("checkGPWS does not fire a huge altitude jump (prevSmoothAlt - currentAlt >= 500) as a callout", () => {
  const w = loadPage();
  const played = [];
  w.playSound = (f) => played.push(f);
  w.checkGPWS(3000, -8);
  w.checkGPWS(400, -8); // huge jump (teleport/aircraft switch), should be suppressed
  assert.equal(played.length, 0);
});
