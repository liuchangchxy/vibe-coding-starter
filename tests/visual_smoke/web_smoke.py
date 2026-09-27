#!/usr/bin/env python3
"""Zero-dependency web smoke gate: static-serve a built SPA, drive headless
Chrome over CDP, screenshot it, and judge whether anything rendered.

Only the Python standard library is used (http.server / socket / zlib /
struct / subprocess) plus a Chrome/Chromium binary. No npm, no pip.

Two verdict layers (the mechanical backstop for "build succeeded but the
page is blank" class incidents):

  1. Identity signals (first) -- the page must be *our* app, not just
     "not blank":
       - build-dir self check (entry file + bootstrap markers + main
         payload files all present, otherwise refuse immediately);
       - main-frame Document HTTP status is 2xx/304 (304 = negotiated
         cache hit, still ours);
       - a main payload script was observed loading successfully;
       - a framework host element exists (e.g. Flutter's flt-glass-pane,
         React's #root -- override with --host-selectors).
  2. Blank-page criterion (after) -- unique screenshot colours < min, or
     the "ink ratio" (pixels differing from the modal colour by > 8 per
     channel) < threshold. Either layer failing exits 1.

"Not blank" alone would pass any contentful non-app page (battle-tested:
a 502 placeholder page passed a colours-only gate), hence layer 1.

Framework mapping (defaults are Flutter; override all three for others):

  React/Vite : --bootstrap-markers vite.svg? no -- use
               --bootstrap-markers 'src/main' --main-candidates 'assets/index-'
               --host-selectors '#root'
  Plain SPA  : --bootstrap-markers '<your boot script>' --main-candidates
               '<your bundle>' --host-selectors '<your mount point>'

Usage:
  python web_smoke.py --dir dist [--chrome <path>] [--timeout 30]
      [--settle 3] [--min-colors 2] [--min-ink 0.005]
      [--bootstrap-markers a.js,b.js] [--main-candidates main.js]
      [--host-selectors '#root'] [--fail-on-errors] [--allow-missing-host]
      [--screenshot out.png] [--selftest]

CI wiring (GitHub Actions): run it right after the web build step; a blank
page turns the job red. Upload the screenshot artifact for forensics.
"""

import argparse
import base64
import binascii
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zlib
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_MIN_COLORS = 2
DEFAULT_MIN_INK_RATIO = 0.005
CHANNEL_TOLERANCE = 8
MAX_SAMPLES = 200000

DEFAULT_BOOTSTRAP_MARKERS = ["flutter_bootstrap.js", "flutter.js"]
DEFAULT_MAIN_CANDIDATES = ["main.dart.js", "main.dart.mjs", "main.dart.wasm"]
DEFAULT_HOST_SELECTORS = ["flt-glass-pane", "flutter-view", "flt-scene-host"]

_MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".wasm": "application/wasm",
    ".css": "text/css; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".map": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}

_CHROME_CANDIDATES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/opt/google/chrome/chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


# ---------------------------------------------------------------- PNG decode


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(data):
    """Decode 8-bit non-interlaced PNG (grey/RGB/grey+alpha/RGBA).

    Returns (width, height, rgba-bytes). Anything else raises loudly --
    never silently downgrade.
    """
    sig = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    if len(data) < 8 or data[:8] != sig:
        raise ValueError("not a PNG (signature mismatch)")
    width = height = bit_depth = color_type = None
    interlace = 0
    idat = bytearray()
    off = 8
    while off + 8 <= len(data):
        (length,) = struct.unpack(">I", data[off:off + 4])
        ctype = data[off + 4:off + 8].decode("ascii", "replace")
        start = off + 8
        if start + length + 4 > len(data):
            raise ValueError("PNG chunk %s truncated" % ctype)
        if ctype == "IHDR":
            if length < 13:
                raise ValueError("IHDR too short")
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB", data[start:start + 10])
            interlace = data[start + 12]
        elif ctype == "IDAT":
            idat += data[start:start + length]
        elif ctype == "IEND":
            break
        off = start + length + 4
    if width is None:
        raise ValueError("PNG missing IHDR")
    if bit_depth != 8:
        raise ValueError("only 8-bit depth supported, got %d" % bit_depth)
    if interlace != 0:
        raise ValueError("interlaced PNG not supported")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise ValueError("unsupported colorType %r" % (color_type,))
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    if len(raw) < (stride + 1) * height:
        raise ValueError("PNG pixel data short")
    rgba = bytearray(width * height * 4)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        f = raw[pos]
        pos += 1
        cur = bytearray(raw[pos:pos + stride])
        pos += stride
        if f == 1:
            for i in range(channels, stride):
                cur[i] = (cur[i] + cur[i - channels]) & 0xFF
        elif f == 2:
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = cur[i - channels] if i >= channels else 0
                cur[i] = (cur[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = cur[i - channels] if i >= channels else 0
                c = prev[i - channels] if i >= channels else 0
                cur[i] = (cur[i] + _paeth(a, prev[i], c)) & 0xFF
        elif f != 0:
            raise ValueError("unknown PNG filter %d" % f)
        for x in range(width):
            s = x * channels
            d = (y * width + x) * 4
            if channels == 1:
                g = cur[s]
                rgba[d:d + 4] = bytes((g, g, g, 255))
            elif channels == 2:
                g = cur[s]
                rgba[d:d + 4] = bytes((g, g, g, cur[s + 1]))
            elif channels == 3:
                rgba[d:d + 4] = bytes((cur[s], cur[s + 1], cur[s + 2], 255))
            else:
                rgba[d:d + 4] = bytes(
                    (cur[s], cur[s + 1], cur[s + 2], cur[s + 3]))
        prev = cur
    return width, height, bytes(rgba)


def analyze_image(width, height, rgba):
    """Sample pixels: unique colour count + ink ratio vs the modal colour."""
    total = width * height
    step = 1 if total <= MAX_SAMPLES else -(-total // MAX_SAMPLES)
    counts = {}
    samples = 0
    for i in range(0, total, step):
        p = i * 4
        c = (rgba[p] << 16) | (rgba[p + 1] << 8) | rgba[p + 2]
        counts[c] = counts.get(c, 0) + 1
        samples += 1
    modal = max(counts, key=counts.get) if counts else 0
    mr, mg, mb = (modal >> 16) & 0xFF, (modal >> 8) & 0xFF, modal & 0xFF
    ink = 0
    for i in range(0, total, step):
        p = i * 4
        if (abs(rgba[p] - mr) > CHANNEL_TOLERANCE
                or abs(rgba[p + 1] - mg) > CHANNEL_TOLERANCE
                or abs(rgba[p + 2] - mb) > CHANNEL_TOLERANCE):
            ink += 1
    return {
        "unique_colors": len(counts),
        "ink_ratio": (ink / samples) if samples else 0.0,
        "samples": samples,
        "modal_color": modal,
    }


def judge(stats, min_colors=DEFAULT_MIN_COLORS,
          min_ink_ratio=DEFAULT_MIN_INK_RATIO):
    """Return None on pass, else a human-readable failure reason."""
    if stats["samples"] == 0:
        return "empty screenshot (0 pixels)"
    if stats["unique_colors"] < min_colors:
        return ("blank page: unique colours %d < %d"
                % (stats["unique_colors"], min_colors))
    if stats["ink_ratio"] < min_ink_ratio:
        return ("blank page: ink ratio %.3f%% < %.3f%% (page is almost all "
                "modal colour #%06x)"
                % (stats["ink_ratio"] * 100, min_ink_ratio * 100,
                   stats["modal_color"]))
    return None


def is_ok_status(status):
    return (200 <= status < 300) or status == 304


# ---------------------------------------------------------------- build check


def verify_build(directory, bootstrap_markers, main_candidates):
    index = os.path.join(directory, "index.html")
    if not os.path.isfile(index):
        return "%s has no index.html: not a web build directory" % directory
    with open(index, encoding="utf-8", errors="replace") as f:
        html = f.read()
    if not any(m in html for m in bootstrap_markers):
        return ("index.html has none of the bootstrap markers (%s): %s is "
                "not our app's web build"
                % ("/".join(bootstrap_markers), directory))
    if not any(os.path.isfile(os.path.join(directory, m))
               for m in main_candidates):
        return ("%s has none of %s: not our app's web build"
                % (directory, " / ".join(main_candidates)))
    return None


# ---------------------------------------------------------------- static server


def _serve_dir(root):
    root = os.path.realpath(root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            try:
                raw = urllib.parse.unquote(
                    self.path.split("?", 1)[0].split("#", 1)[0])
                # %2f decodes to "/" inside a segment -- split first, then
                # reject every dot / separator segment, then realpath-check.
                segs = raw.split("/")
                if any(s in (".", "..") or "/" in s or "\\" in s
                       for s in segs):
                    self.send_error(404)
                    return
                path = os.path.realpath(os.path.join(root, *segs))
                if os.path.commonpath([root, path]) != root:
                    self.send_error(404)
                    return
                if os.path.isdir(path):
                    path = os.path.join(path, "index.html")
                if not os.path.isfile(path):
                    self.send_error(404)
                    return
                ext = os.path.splitext(path)[1].lower()
                with open(path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type",
                                 _MIME.get(ext, "application/octet-stream"))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception:
                try:
                    self.send_error(400)
                except Exception:
                    pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ---------------------------------------------------------------- minimal CDP client (stdlib only)


class CdpError(Exception):
    pass


class _Ws:
    def __init__(self, url):
        parts = urllib.parse.urlparse(url)
        self._sock = socket.create_connection(
            (parts.hostname, parts.port or 80), timeout=10)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
               "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
               "Sec-WebSocket-Version: 13\r\n\r\n"
               % (parts.path or "/", parts.hostname, key))
        self._sock.sendall(req.encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise CdpError("websocket handshake failed")
            head += chunk
        if b"101" not in head.split(b"\r\n", 1)[0]:
            raise CdpError("websocket handshake rejected: %r" % head[:60])
        self._buf = head.split(b"\r\n\r\n", 1)[1]
        self._closed = False

    def _read_exact(self, n):
        while len(self._buf) < n:
            chunk = self._sock.recv(max(4096, n - len(self._buf)))
            if not chunk:
                raise CdpError("websocket closed mid-frame")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def _send_frame(self, opcode, payload):
        head = bytes([0x80 | opcode])
        ln = len(payload)
        mask = os.urandom(4)
        if ln < 126:
            head += bytes([0x80 | ln])
        elif ln < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", ln)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", ln)
        self._sock.sendall(head + mask + bytes(
            b ^ mask[i % 4] for i, b in enumerate(payload)))

    def send_text(self, text):
        self._send_frame(0x1, text.encode())

    def recv_message(self):
        """Next complete text message; handles fragmentation + ping."""
        chunks = []
        while True:
            b1, b2 = self._read_exact(2)
            opcode = b1 & 0x0F
            ln = b2 & 0x7F
            if ln == 126:
                (ln,) = struct.unpack(">H", self._read_exact(2))
            elif ln == 127:
                (ln,) = struct.unpack(">Q", self._read_exact(8))
            if b2 & 0x80:
                mask = self._read_exact(4)
            else:
                mask = None
            payload = self._read_exact(ln)
            if mask:
                payload = bytes(
                    b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x8:
                self._closed = True
                raise CdpError("websocket closed by peer")
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode in (0x0, 0x1):
                chunks.append(payload)
                if b1 & 0x80:
                    return b"".join(chunks).decode("utf-8", "replace")

    def close(self):
        try:
            self._send_frame(0x8, b"")
        except Exception:
            pass
        try:
            self._sock.close()
        except Exception:
            pass


class Cdp:
    def __init__(self, url):
        self._ws = _Ws(url)
        self._next_id = 1
        self._pending = {}
        self._events = deque()
        self._lock = threading.Lock()
        self._dead = None
        self._thread = threading.Thread(target=self._pump, daemon=True)
        self._thread.start()

    def _pump(self):
        try:
            while True:
                msg = json.loads(self._ws.recv_message())
                with self._lock:
                    if "id" in msg:
                        box = self._pending.pop(msg["id"], None)
                        if box is not None:
                            box.append(msg)
                            box[0].set()
                    else:
                        self._events.append(msg)
        except Exception as e:
            with self._lock:
                self._dead = e
                for box in self._pending.values():
                    box[0].set()

    def send(self, method, params=None, timeout=30):
        with self._lock:
            if self._dead is not None:
                raise CdpError("CDP connection dead: %r" % (self._dead,))
            call_id = self._next_id
            self._next_id += 1
            box = [threading.Event()]
            self._pending[call_id] = box
        payload = {"id": call_id, "method": method}
        if params:
            payload["params"] = params
        self._ws.send_text(json.dumps(payload))
        if not box[0].wait(timeout):
            with self._lock:
                self._pending.pop(call_id, None)
            raise CdpError("CDP %s timed out" % method)
        with self._lock:
            if self._dead is not None and not box[1:]:
                raise CdpError("CDP connection dead: %r" % (self._dead,))
            msg = box[1]
        if "error" in msg:
            raise CdpError("CDP %s: %s" % (method, msg["error"]))
        return msg.get("result", {})

    def drain_events(self):
        with self._lock:
            out = list(self._events)
            self._events.clear()
            return out

    def close(self):
        self._ws.close()


# ---------------------------------------------------------------- chrome


def find_chrome(explicit=None):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    env = os.environ.get("CHROME_EXECUTABLE")
    if env and os.path.isfile(env):
        return env
    for name in ("google-chrome", "google-chrome-stable",
                 "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    for path in _CHROME_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def _wait_page_target(debug_port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/json/list" % debug_port,
                    timeout=5) as r:
                for t in json.loads(r.read().decode()):
                    if t.get("type") == "page" and t.get(
                            "webSocketDebuggerUrl"):
                        return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.25)
    return None


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# ---------------------------------------------------------------- main flow


def run_smoke(opts):
    errors = []
    build_error = verify_build(opts["dir"], opts["bootstrap_markers"],
                               opts["main_candidates"])
    if build_error:
        return {"stats": None, "failure": build_error, "errors": errors,
                "screenshot": None}
    chrome = find_chrome(opts.get("chrome"))
    if not chrome:
        return {"stats": None,
                "failure": "Chrome not found: set CHROME_EXECUTABLE or pass "
                           "--chrome", "errors": errors, "screenshot": None}

    server = _serve_dir(opts["dir"])
    app_port = server.server_address[1]
    debug_port = _free_port()
    tmp = tempfile.mkdtemp(prefix="web_smoke_")
    proc = None
    client = None
    shot_path = None
    try:
        proc = subprocess.Popen(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--disable-dev-shm-usage", "--hide-scrollbars",
             "--no-first-run", "--no-default-browser-check",
             "--user-data-dir=" + tmp,
             "--remote-debugging-port=%d" % debug_port, "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ws_url = _wait_page_target(debug_port, opts["timeout"])
        if not ws_url:
            return {"stats": None,
                    "failure": "Chrome not ready in %ds (--headless=new "
                               "unsupported by this version?)" % opts["timeout"],
                    "errors": errors, "screenshot": None}
        client = Cdp(ws_url)
        client.send("Page.enable")
        client.send("Runtime.enable")
        client.send("Log.enable")
        client.send("Network.enable")
        client.send("Emulation.setDeviceMetricsOverride",
                    {"width": 1280, "height": 900, "deviceScaleFactor": 1,
                     "mobile": False})
        nav = client.send("Page.navigate",
                          {"url": "http://127.0.0.1:%d/index.html" % app_port})
        if nav.get("errorText"):
            return {"stats": None,
                    "failure": "navigation failed: %s" % nav["errorText"],
                    "errors": errors, "screenshot": None}
        main_frame = nav.get("frameId")

        # Wait for load (poll events; warn and continue on timeout).
        deadline = time.time() + opts["timeout"]
        loaded = False
        doc_statuses = []
        payload_hits = []
        payload_markers = (list(opts["main_candidates"])
                           + list(opts["bootstrap_markers"]))
        while time.time() < deadline and not loaded:
            for ev in client.drain_events():
                _absorb_event(ev, main_frame, doc_statuses, payload_markers,
                              payload_hits, errors)
                if ev.get("method") == "Page.loadEventFired":
                    loaded = True
            time.sleep(0.2)
        if not loaded:
            print("warning: Page.loadEventFired timeout, screenshotting anyway")
        # Drain once more so late Network events are not missed.
        for ev in client.drain_events():
            _absorb_event(ev, main_frame, doc_statuses, payload_markers,
                          payload_hits, errors)

        # Identity signals: the page must be OUR app, not just "not blank".
        if not doc_statuses:
            return {"stats": None,
                    "failure": "no main-frame Document response observed -- "
                               "CDP Network behaviour may have changed, the "
                               "criterion silently degraded; refusing green",
                    "errors": errors, "screenshot": None}
        if not any(is_ok_status(s) for s in doc_statuses):
            return {"stats": None,
                    "failure": "main Document HTTP status %s (not 2xx/304)"
                               % "/".join(map(str, doc_statuses)),
                    "errors": errors, "screenshot": None}
        if not payload_hits:
            return {"stats": None,
                    "failure": "no main payload script (%s) observed loading "
                               "-- this page is not our app"
                               % " / ".join(payload_markers),
                    "errors": errors, "screenshot": None}
        if opts["host_selectors"] and not opts["allow_missing_host"]:
            expr = ("document.querySelector('%s') !== null"
                    % ", ".join(opts["host_selectors"]))
            deadline = time.time() + opts["timeout"]
            ready = False
            while time.time() < deadline:
                try:
                    res = client.send(
                        "Runtime.evaluate",
                        {"expression": expr, "returnByValue": True})
                    if res.get("result", {}).get("value") is True:
                        ready = True
                        break
                except CdpError as e:
                    print("host probe failed: %s" % e)
                time.sleep(0.25)
            if not ready:
                return {"stats": None,
                        "failure": "no host element (%s) detected; pass "
                                   "--allow-missing-host if the framework "
                                   "renamed its mount point"
                                   % ", ".join(opts["host_selectors"]),
                        "errors": errors, "screenshot": None}
        time.sleep(opts["settle"])

        shot = client.send("Page.captureScreenshot", {"format": "png"})
        raw = base64.b64decode(shot["data"])
        if opts.get("screenshot"):
            with open(opts["screenshot"], "wb") as f:
                f.write(raw)
            shot_path = opts["screenshot"]
        w, h, rgba = decode_png(raw)
        stats = analyze_image(w, h, rgba)
        return {"stats": stats,
                "failure": judge(stats, opts["min_colors"],
                                 opts["min_ink_ratio"]),
                "errors": errors, "screenshot": shot_path}
    except Exception as e:  # never let the harness die silently
        return {"stats": None, "failure": "smoke blew up: %r" % (e,),
                "errors": errors, "screenshot": shot_path}
    finally:
        if client is not None:
            client.close()
        if proc is not None:
            proc.kill()
        server.shutdown()
        server.server_close()
        if not opts.get("keep_temp"):
            shutil.rmtree(tmp, ignore_errors=True)


def _absorb_event(ev, main_frame, doc_statuses, payload_markers,
                  payload_hits, errors):
    method = ev.get("method")
    params = ev.get("params", {}) or {}
    if method == "Network.responseReceived":
        resp = params.get("response", {}) or {}
        url = resp.get("url", "")
        status = resp.get("status", 0) or 0
        # Only the MAIN frame's Document counts: type == 'Document' also
        # covers iframes, otherwise a 200 child could vouch for a 500 page.
        if (params.get("type") == "Document"
                and (main_frame is None
                     or params.get("frameId") == main_frame)):
            doc_statuses.append(status)
        if any(m in url for m in payload_markers) and is_ok_status(status):
            payload_hits.append(url)
    elif method == "Runtime.consoleAPICalled":
        if params.get("type") == "error":
            args = " ".join(str(a.get("value", a.get("description", "")))
                            for a in params.get("args", []))
            errors.append("console.error: %s" % args)
    elif method == "Runtime.exceptionThrown":
        det = params.get("exceptionDetails", {}) or {}
        exc = det.get("exception", {}) or {}
        errors.append("uncaught: %s" % (exc.get("description")
                                        or det.get("text", "unknown")))
    elif method == "Log.entryAdded":
        entry = params.get("entry", {}) or {}
        if entry.get("level") == "error":
            errors.append("log: %s" % entry.get("text", ""))


def main(argv=None):
    import argparse as _ap
    ap = _ap.ArgumentParser(
        description="Zero-dependency web smoke gate (blank page = red).")
    ap.add_argument("--dir", required=False,
                    help="built web directory (must contain index.html)")
    ap.add_argument("--chrome", default=None)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--settle", type=int, default=3)
    ap.add_argument("--min-colors", type=int, default=DEFAULT_MIN_COLORS)
    ap.add_argument("--min-ink", type=float, default=DEFAULT_MIN_INK_RATIO)
    ap.add_argument("--bootstrap-markers",
                    default=",".join(DEFAULT_BOOTSTRAP_MARKERS))
    ap.add_argument("--main-candidates",
                    default=",".join(DEFAULT_MAIN_CANDIDATES))
    ap.add_argument("--host-selectors",
                    default=",".join(DEFAULT_HOST_SELECTORS))
    ap.add_argument("--fail-on-errors", action="store_true")
    ap.add_argument("--allow-missing-host", action="store_true")
    ap.add_argument("--keep-temp", action="store_true")
    ap.add_argument("--screenshot", default=None)
    ap.add_argument("--selftest", action="store_true",
                    help="prove the gate can go red AND green, then exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return 0 if selftest() else 1
    if not args.dir or not os.path.isdir(args.dir):
        ap.error("--dir must be an existing directory")

    opts = {
        "dir": args.dir,
        "chrome": args.chrome,
        "timeout": args.timeout,
        "settle": args.settle,
        "min_colors": args.min_colors,
        "min_ink_ratio": args.min_ink,
        "bootstrap_markers": [x for x in args.bootstrap_markers.split(",")
                              if x],
        "main_candidates": [x for x in args.main_candidates.split(",") if x],
        "host_selectors": [x for x in args.host_selectors.split(",") if x],
        "fail_on_errors": args.fail_on_errors,
        "allow_missing_host": args.allow_missing_host,
        "keep_temp": args.keep_temp,
        "screenshot": args.screenshot,
    }
    outcome = run_smoke(opts)
    stats = outcome["stats"]
    if stats:
        print("web smoke: %d samples / %d unique colours / ink %.2f%% / "
              "modal #%06x" % (stats["samples"], stats["unique_colors"],
                               stats["ink_ratio"] * 100,
                               stats["modal_color"]))
    if outcome["screenshot"]:
        print("screenshot: %s" % outcome["screenshot"])
    for e in outcome["errors"][:20]:
        print("  page error: %s" % e)
    if outcome["failure"]:
        print("FAIL: %s" % outcome["failure"], file=sys.stderr)
        return 1
    if opts["fail_on_errors"] and outcome["errors"]:
        print("FAIL: %d page error(s) (--fail-on-errors)"
              % len(outcome["errors"]), file=sys.stderr)
        return 1
    print("PASS: page rendered content")
    return 0


# ---------------------------------------------------------------- selftest
# A gate that never went red is a ritual, not a gate. --selftest proves the
# PNG codec round-trips, the judge rejects blank and accepts contentful,
# and the build-dir check refuses non-app directories.


def _encode_png(width, height, rgba):
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgba[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw))

    def chunk(ctype, payload):
        return (struct.pack(">I", len(payload)) + ctype + payload
                + struct.pack(">I", binascii.crc32(ctype + payload)
                              & 0xFFFFFFFF))

    sig = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) \
        + chunk(b"IEND", b"")


def selftest():
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  [ok]   selftest: %s" % name)
        else:
            failed += 1
            print("  [FAIL] selftest: %s" % name)

    print("web smoke selftest")
    # 1. codec round-trip on a colourful image
    w, h = 64, 40
    rgba = bytearray()
    for y in range(h):
        for x in range(w):
            rgba += bytes((x * 4 % 256, y * 6 % 256, (x + y) % 256, 255))
    w2, h2, out = decode_png(_encode_png(w, h, bytes(rgba)))
    check("png round-trip", (w2, h2, out) == (w, h, bytes(rgba)))
    stats = analyze_image(w2, h2, out)
    check("colourful passes judge",
          judge(stats) is None and stats["unique_colors"] > 100)
    # 2. pure white fails
    white = bytes([255, 255, 255, 255]) * (16 * 16)
    w3, h3, out3 = decode_png(_encode_png(16, 16, white))
    rej = judge(analyze_image(w3, h3, out3))
    check("pure white rejected", rej is not None and "unique colours" in rej)
    # 3. sparse-but-real content fails the ink gate (documented heuristic)
    mostly = bytearray(bytes([255, 255, 255, 255]) * (100 * 100))
    mostly[0:4] = bytes((0, 0, 0, 255))
    rej2 = judge(analyze_image(
        *decode_png(_encode_png(100, 100, bytes(mostly)))))
    check("near-blank rejected by ink ratio",
          rej2 is not None and "ink ratio" in rej2)
    # 4. codec refuses exotic PNGs loudly
    try:
        decode_png(b"definitely not a png file.............")
        check("non-png refused", False)
    except ValueError:
        check("non-png refused", True)
    # 5. build-dir check
    tmp = tempfile.mkdtemp(prefix="web_smoke_st_")
    try:
        os.makedirs(os.path.join(tmp, "empty"))
        check("dir without index refused",
              verify_build(os.path.join(tmp, "empty"), ["boot.js"],
                           ["main.js"]) is not None)
        d = os.path.join(tmp, "fake")
        os.makedirs(d)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write("<html><body>hello</body></html>")
        check("non-app index refused",
              verify_build(d, ["boot.js"], ["main.js"]) is not None)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write('<script src="boot.js"></script>')
        with open(os.path.join(d, "main.js"), "w") as f:
            f.write("console.log(1)")
        check("valid app dir accepted",
              verify_build(d, ["boot.js"], ["main.js"]) is None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(("PASS" if failed == 0 else "FAIL")
          + ": selftest %d passed, %d failed" % (passed, failed))
    return failed == 0


if __name__ == "__main__":
    sys.exit(main())
