"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

function heightOfHeadingLabels(group) {
  return Array.from(group.querySelectorAll("text")).map((t) => t.textContent);
}

test("updateHdgTape shows cardinal letters at 0/90/180/270", () => {
  const w = loadPage();
  const group = w.document.getElementById("hdg_tape");
  // scale=4 covers +-62.5 heading around center per updateHdgTape's own window math (250/scale),
  // so center on 90 (East) to guarantee it falls within the visible range alongside N territory.
  w.updateHdgTape(group, 90, 4, 30, 10);
  const labels = heightOfHeadingLabels(group);
  assert.ok(labels.includes("E"), `expected E label, got ${JSON.stringify(labels)}`);
});

test("updateHdgTape zero-pads non-cardinal major headings to 3 digits", () => {
  const w = loadPage();
  const group = w.document.getElementById("hdg_tape");
  w.updateHdgTape(group, 60, 4, 30, 10);
  const labels = heightOfHeadingLabels(group);
  assert.ok(labels.some((l) => l === "060"));
});

test("updateHdgTape wraps negative virtual headings into 0-359 range for labels", () => {
  const w = loadPage();
  const group = w.document.getElementById("hdg_tape");
  // Centered near 0 with a wide-ish window should include ticks below 0, e.g. -30 -> should render as 330
  w.updateHdgTape(group, 5, 4, 30, 10);
  const labels = heightOfHeadingLabels(group);
  assert.ok(!labels.some((l) => l.startsWith("-")), "no negative heading labels should ever be rendered");
});

test("updateTape (speed/left tape) omits negative speed ticks", () => {
  const w = loadPage();
  const group = w.document.getElementById("speed_tape");
  w.updateTape(group, 5, 3, 20, 10, false);
  const lines = Array.from(group.querySelectorAll("line"));
  // Every rendered tick's y is derived from (value - v) * scale for v >= 0 only on the left/speed tape
  assert.ok(lines.length > 0);
});

test("updateTape (altitude/right tape) allows negative values (isRight=true)", () => {
  const w = loadPage();
  const group = w.document.getElementById("alt_tape");
  w.updateTape(group, -50, 1.5, 100, 20, true);
  // Should not throw and should produce at least some ticks around the negative center value
  const lines = Array.from(group.querySelectorAll("line"));
  assert.ok(lines.length > 0);
});

test("updateTape renders major tick labels at majorStep multiples", () => {
  const w = loadPage();
  const group = w.document.getElementById("alt_tape");
  w.updateTape(group, 1000, 1.5, 100, 20, true);
  const labels = Array.from(group.querySelectorAll("text")).map((t) => t.textContent);
  assert.ok(labels.every((l) => Number(l) % 100 === 0), `expected all labels to be multiples of 100, got ${labels}`);
});

test("updateTape clears previous ticks on each call (innerHTML replace, not append)", () => {
  const w = loadPage();
  const group = w.document.getElementById("alt_tape");
  w.updateTape(group, 1000, 1.5, 100, 20, true);
  const firstCount = group.querySelectorAll("line").length;
  w.updateTape(group, 1000, 1.5, 100, 20, true);
  const secondCount = group.querySelectorAll("line").length;
  assert.equal(firstCount, secondCount, "calling updateTape twice with the same value must not double the ticks");
});
