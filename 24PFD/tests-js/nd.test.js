"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

test("buildNdRose draws all 36 ticks with 12 major cardinal/numeric labels", () => {
  const w = loadPage();
  w.buildNdRose();
  const rose = w.document.getElementById("nd_rose");
  const lines = rose.querySelectorAll("line");
  const texts = rose.querySelectorAll("text");
  assert.equal(lines.length, 36, `expected 36 ticks (every 10deg), got ${lines.length}`);
  assert.equal(texts.length, 12, `expected 12 major labels (every 30deg), got ${texts.length}`);
});

test("buildNdRose labels cardinal directions N/E/S/W instead of numbers", () => {
  const w = loadPage();
  w.buildNdRose();
  const labels = Array.from(w.document.getElementById("nd_rose").querySelectorAll("text")).map(t => t.textContent);
  assert.ok(labels.includes("N"));
  assert.ok(labels.includes("E"));
  assert.ok(labels.includes("S"));
  assert.ok(labels.includes("W"));
});

test("updateNd rotates the rose opposite to heading (heading-up display)", () => {
  const w = loadPage();
  w.eval("smoothState.heading = 90;");
  w.updateNd();
  const transform = w.document.getElementById("nd_rose").getAttribute("transform");
  assert.equal(transform, "rotate(-90)");
});

test("updateNd updates the digital heading readout, zero-padded", () => {
  const w = loadPage();
  w.eval("smoothState.heading = 7;");
  w.updateNd();
  assert.equal(w.document.getElementById("nd_hdg_text").textContent, "007");
});

test("updateNd shows heading 360 as 000", () => {
  const w = loadPage();
  w.eval("smoothState.heading = 360;");
  w.updateNd();
  assert.equal(w.document.getElementById("nd_hdg_text").textContent, "000");
});

test("updateNd only builds the rose geometry once across repeated calls", () => {
  const w = loadPage();
  w.updateNd();
  const firstLineCount = w.document.getElementById("nd_rose").querySelectorAll("line").length;
  w.updateNd();
  w.updateNd();
  const secondLineCount = w.document.getElementById("nd_rose").querySelectorAll("line").length;
  assert.equal(firstLineCount, secondLineCount, "rose ticks must not accumulate/duplicate on repeated updateNd calls");
});

test("updateFailFlags shows ND fail banner when relay is disconnected", () => {
  const w = loadPage();
  w.eval("wsConnected = false;");
  w.updateFailFlags();
  assert.equal(w.document.getElementById("nd_fail_banner").style.display, "block");
});

test("updateFailFlags shows ND 'select aircraft' prompt when connected but no callsign chosen", () => {
  const w = loadPage();
  w.eval("wsConnected = true; activeCallsign = null;");
  w.updateFailFlags();
  assert.equal(w.document.getElementById("nd_fail_banner").style.display, "none");
  assert.equal(w.document.getElementById("nd_no_aircraft_prompt").style.display, "block");
});
