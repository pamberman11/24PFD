"use strict";
/**
 * Loads graphicsvg.html into a real jsdom document with scripts executed,
 * stubbing out browser APIs the page relies on that don't exist / don't make
 * sense in a headless test run (WebSocket, Audio, matchMedia, requestAnimationFrame).
 *
 * Returns the jsdom `window`. Because the page's top-level `let`/`const`
 * declarations (smoothState, aircraftState, activeCallsign, ...) live in the
 * window's global lexical scope rather than as `window.*` properties, tests
 * must reach them via `window.eval("...")` (indirect eval), not window.foo.
 * Plain `function` declarations (update, updateTape, checkGPWS, ...) ARE
 * attached to window and can be called directly.
 */
const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const HTML_PATH = path.join(__dirname, "..", "graphicsvg.html");

class StubWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 0;
    // Intentionally never "connects" - tests drive state directly instead of
    // simulating real server messages, keeping tests hermetic/offline.
  }
  send() {}
  close() {}
}

class StubAudio {
  constructor(src) {
    this.src = src;
  }
  play() {
    return Promise.resolve();
  }
}

function loadPage({ storedLighting } = {}) {
  const html = fs.readFileSync(HTML_PATH, "utf8");

  const dom = new JSDOM(html, {
    url: "http://localhost/",
    runScripts: "dangerously",
    resources: "usable",
    beforeParse(window) {
      window.WebSocket = StubWebSocket;
      window.Audio = StubAudio;
      window.matchMedia = () => ({
        matches: false,
        addListener() {},
        removeListener() {},
      });
      window.requestAnimationFrame = () => 0; // never auto-fires; tests call update()/renderLoop() explicitly
      if (storedLighting) {
        window.localStorage.setItem("lighting", storedLighting);
      }
    },
  });

  return dom.window;
}

module.exports = { loadPage, StubWebSocket, StubAudio };
