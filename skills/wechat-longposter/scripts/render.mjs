#!/usr/bin/env node
// Render a fixed-width HTML poster to a full-height PNG via Chrome headless + CDP.
// Usage: node render.mjs <input.html> <output.png> [--width 1080] [--chrome PATH]
// Requires Node 22+ (global WebSocket and fetch).

import { spawn, execFileSync } from "node:child_process";
import { access, mkdtemp, readFile, rm, stat, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { once } from "node:events";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { setTimeout as sleep } from "node:timers/promises";

const USAGE = `usage: node render.mjs <input.html> <output.png> [--width 1080] [--chrome PATH]

  --width   canvas width in CSS pixels (default 1080)
  --chrome  Chrome/Chromium binary; also reads CHROME_BIN
`;

function parseArgs(argv) {
  const out = { width: 1080, chrome: null, input: null, output: null };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--width") out.width = Number(argv[++i]);
    else if (arg === "--chrome") out.chrome = argv[++i];
    else if (arg === "-h" || arg === "--help") {
      process.stdout.write(USAGE);
      process.exit(0);
    } else if (!out.input) out.input = arg;
    else if (!out.output) out.output = arg;
    else throw new Error(`unexpected argument: ${arg}`);
  }
  if (!out.input || !out.output) throw new Error("input and output are required\n" + USAGE);
  if (!Number.isInteger(out.width) || out.width < 320) throw new Error("--width must be an integer >= 320");
  return out;
}

async function executable(path) {
  try {
    await access(path, constants.X_OK);
    return path;
  } catch {
    return null;
  }
}

async function findChrome(explicit) {
  const candidates = [];
  if (explicit) candidates.push(explicit);
  if (process.env.CHROME_BIN) candidates.push(process.env.CHROME_BIN);
  candidates.push(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium"
  );
  for (const candidate of candidates) {
    if (candidate.includes("/")) {
      const found = await executable(candidate);
      if (found) return found;
    } else {
      try {
        return execFileSync("which", [candidate], { encoding: "utf8" }).trim();
      } catch {}
    }
  }
  for (const name of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"]) {
    try {
      return execFileSync("which", [name], { encoding: "utf8" }).trim();
    } catch {}
  }
  throw new Error("Chrome/Chromium not found; pass --chrome PATH or set CHROME_BIN");
}

class Cdp {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.seq = 0;
    this.pending = new Map();
    this.events = new Map();
  }

  async open() {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("CDP websocket open timed out")), 10_000);
      this.ws.onopen = () => {
        clearTimeout(timer);
        resolve();
      };
      this.ws.onerror = (event) => {
        clearTimeout(timer);
        reject(new Error(`CDP websocket error: ${event?.message ?? "unknown"}`));
      };
    });
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(JSON.stringify(message.error)));
        else resolve(message.result);
      } else if (message.method) {
        const waiters = this.events.get(message.method);
        if (waiters) {
          this.events.delete(message.method);
          for (const waiter of waiters) waiter(message.params);
        }
      }
    };
    this.ws.onclose = () => {
      for (const { reject } of this.pending.values()) reject(new Error("CDP websocket closed"));
      this.pending.clear();
    };
  }

  send(method, params = {}) {
    const id = ++this.seq;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }

  once(method) {
    return new Promise((resolve) => {
      const waiters = this.events.get(method) ?? [];
      waiters.push(resolve);
      this.events.set(method, waiters);
    });
  }

  close() {
    try {
      this.ws.close();
    } catch {}
  }
}

async function waitForFile(path, timeoutMs = 20_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const text = await readFile(path, "utf8");
      const port = Number(text.split("\n")[0]);
      if (port > 0) return port;
    } catch {}
    await sleep(100);
  }
  throw new Error(`Chrome DevTools did not start (waited for ${path})`);
}

async function waitForPage(port, timeoutMs = 10_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const page = targets.find((target) => target.type === "page");
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(100);
  }
  throw new Error("Chrome DevTools has no page target");
}

function pngSize(buffer) {
  const signature = "89504e470d0a1a0a";
  if (buffer.subarray(0, 8).toString("hex") !== signature) {
    throw new Error("rendered output is not a PNG");
  }
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = resolve(args.input);
  const output = resolve(args.output);
  const chromeBin = await findChrome(args.chrome);
  const profile = await mkdtemp(join(tmpdir(), "poster-chrome-"));
  let chrome;
  let cdp;

  try {
    chrome = spawn(
      chromeBin,
      [
        "--headless=new",
        "--remote-debugging-port=0",
        `--user-data-dir=${profile}`,
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1080,1200",
        "about:blank",
      ],
      { stdio: "ignore" }
    );

    const port = await waitForFile(join(profile, "DevToolsActivePort"));
    const wsUrl = await waitForPage(port);
    cdp = new Cdp(wsUrl);
    await cdp.open();

    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: args.width,
      height: 1200,
      deviceScaleFactor: 1,
      mobile: false,
    });

    const loaded = cdp.once("Page.loadEventFired");
    await cdp.send("Page.navigate", { url: pathToFileURL(input).href });
    await loaded;

    const measured = await cdp.send("Runtime.evaluate", {
      expression: `document.fonts.ready.then(() => new Promise((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(() => resolve({
          width: document.documentElement.scrollWidth,
          height: document.documentElement.scrollHeight
        })));
      }))`,
      awaitPromise: true,
      returnByValue: true,
    });
    const { width, height } = measured.result.value;
    if (!height || !width) throw new Error("could not measure document size");
    if (width > args.width + 1) {
      throw new Error(`content is ${width}px wide but canvas is ${args.width}px; fix horizontal overflow`);
    }

    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: args.width,
      height,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await cdp.send("Runtime.evaluate", { expression: "window.scrollTo(0, 0)" });
    await sleep(300);

    const shot = await cdp.send("Page.captureScreenshot", {
      format: "png",
      fromSurface: true,
      captureBeyondViewport: true,
      clip: { x: 0, y: 0, width: args.width, height, scale: 1 },
    });
    const buffer = Buffer.from(shot.data, "base64");
    const actual = pngSize(buffer);
    if (actual.width !== args.width || actual.height !== height) {
      throw new Error(`PNG is ${actual.width}x${actual.height}, expected ${args.width}x${height}`);
    }
    await writeFile(output, buffer);
    const bytes = (await stat(output)).size;
    process.stdout.write(`rendered ${actual.width}x${actual.height} -> ${output} (${Math.round(bytes / 1024)} KB)\n`);
  } finally {
    cdp?.close();
    if (chrome && chrome.exitCode === null) {
      chrome.kill("SIGTERM");
      await Promise.race([once(chrome, "exit"), sleep(2_000)]);
      if (chrome.exitCode === null) chrome.kill("SIGKILL");
    }
    await rm(profile, { recursive: true, force: true });
  }
}

main().catch((error) => {
  process.stderr.write(`poster: ${error.message}\n`);
  process.exitCode = 1;
});
