"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { loadPage } = require("./dom-harness.js");

function seedCallsigns(w, callsigns) {
  w.eval(`
    const select = document.getElementById("callsignSelect");
    ${JSON.stringify(callsigns)}.forEach((cs) => {
      const opt = document.createElement("option");
      opt.value = cs; opt.textContent = cs;
      select.appendChild(opt);
    });
  `);
}

function visibleCallsigns(w) {
  return Array.from(w.document.querySelectorAll("#callsignSelect option"))
    .filter((o) => !o.hidden && o.value !== "")
    .map((o) => o.value);
}

test("filterCallsigns shows only options matching the query", () => {
  const w = loadPage();
  seedCallsigns(w, ["DAL-123", "UAE-456", "DAL-789"]);
  w.eval(`document.getElementById("callsignSearch").value = "DAL";`);
  w.filterCallsigns();
  assert.deepEqual(visibleCallsigns(w), ["DAL-123", "DAL-789"]);
});

test("filterCallsigns matching is case-insensitive", () => {
  const w = loadPage();
  seedCallsigns(w, ["DAL-123", "UAE-456"]);
  w.eval(`document.getElementById("callsignSearch").value = "dal-12";`);
  w.filterCallsigns();
  assert.deepEqual(visibleCallsigns(w), ["DAL-123"]);
});

test("clearing the search restores every option", () => {
  const w = loadPage();
  seedCallsigns(w, ["DAL-123", "UAE-456"]);
  w.eval(`document.getElementById("callsignSearch").value = "UAE";`);
  w.filterCallsigns();
  w.eval(`document.getElementById("callsignSearch").value = "";`);
  w.filterCallsigns();
  assert.deepEqual(visibleCallsigns(w), ["DAL-123", "UAE-456"]);
});

test("filterCallsigns never hides the currently tracked callsign and keeps the selection stable", () => {
  const w = loadPage();
  seedCallsigns(w, ["DAL-123", "UAE-456"]);
  w.eval(`
    document.getElementById("callsignSelect").value = "UAE-456";
    document.getElementById("callsignSearch").value = "DAL";
  `);
  w.filterCallsigns();
  const uaeOpt = Array.from(w.document.querySelectorAll("#callsignSelect option"))
    .find((o) => o.value === "UAE-456");
  assert.equal(uaeOpt.hidden, false);
  assert.equal(w.document.getElementById("callsignSelect").value, "UAE-456");
});
