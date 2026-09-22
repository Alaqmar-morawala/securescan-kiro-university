"""Screenshot-driven capture: pump() grabs a frame every ~0.13s for a faithful timeline."""
import base64
import json
import time
import urllib.request

import websocket


class Page:
    def __init__(self, host="127.0.0.1", port=9222):
        self.handlers = {}
        self.frames = []          # (timestamp, jpeg_bytes)
        self.responses = {}
        self.capture = False
        self.period = 0.13
        self._next_capture = 0.0
        for _ in range(40):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://{host}:{port}/json"))
                page = [t for t in tabs if t.get("type") == "page"]
                if page:
                    self.ws = websocket.create_connection(page[0]["webSocketDebuggerUrl"], timeout=30)
                    self.ws.settimeout(0.2)
                    self.i = 0
                    self.send("Page.enable")
                    self.send("Runtime.enable")
                    return
            except Exception:
                pass
            time.sleep(0.5)
        raise RuntimeError("no CDP page target")

    # ---------- plumbing ----------
    def _dispatch(self, msg):
        h = self.handlers.get(msg.get("method", ""))
        if h:
            h(msg.get("params", {}))

    def _on_frame(self, params):
        try:
            self.frames.append((time.time(), base64.b64decode(params["data"])))
        except Exception:
            pass
        # ack without waiting for a response (keeps the read loop single-owner)
        try:
            self.i += 1
            self.ws.send(json.dumps({
                "id": self.i, "method": "Page.screencastFrameAck",
                "params": {"sessionId": params["sessionId"]},
            }))
        except Exception:
            pass

    def _read(self, timeout=0.2):
        """Single owner of recv(): dispatch events, stash responses by id."""
        self.ws.settimeout(timeout)
        msg = json.loads(self.ws.recv())
        if "id" in msg:
            self.responses[msg["id"]] = msg
        else:
            self._dispatch(msg)

    def send(self, method, **params):
        self.i += 1
        rid = self.i
        self.ws.send(json.dumps({"id": rid, "method": method, "params": params}))
        deadline = time.time() + 60
        while rid not in self.responses:
            try:
                self._read(timeout=0.2)
            except websocket.WebSocketTimeoutException:
                if time.time() > deadline:
                    raise RuntimeError(f"timeout waiting for {method}")
            except Exception:
                time.sleep(0.02)
        msg = self.responses.pop(rid)
        if "error" in msg:
            raise RuntimeError(f"{method}: {msg['error']}")
        return msg.get("result", {})

    def pump(self, seconds):
        """Drain events AND grab a screenshot frame every `period` seconds."""
        end = time.time() + seconds
        while time.time() < end:
            now = time.time()
            if self.capture and now >= self._next_capture:
                self._next_capture = now + self.period
                self.grab()
            try:
                self._read(timeout=min(0.1, max(0.01, end - time.time())))
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                time.sleep(0.01)

    def grab(self):
        try:
            r = self.send("Page.captureScreenshot", format="jpeg", quality=82)
            self.frames.append((time.time(), base64.b64decode(r["data"])))
        except Exception:
            pass

    def start_recording(self):
        self.frames = []
        self.capture = True
        self._next_capture = time.time()

    def stop_and_write(self, out_dir):
        """Save JPEG frames + concat list honoring real capture timestamps."""
        import os

        self.capture = False
        self.grab()
        os.makedirs(out_dir, exist_ok=True)
        n = len(self.frames)
        if n == 0:
            raise RuntimeError("no frames captured")
        lines = []
        for idx, (ts, data) in enumerate(self.frames):
            name = f"f{idx:05d}.jpg"
            with open(os.path.join(out_dir, name), "wb") as fh:
                fh.write(data)
            nxt = self.frames[idx + 1][0] if idx + 1 < n else ts + 0.2
            dur = min(max(nxt - ts, 1 / 30.0), 0.25)
            lines.append(f"file '{name}'")
            lines.append(f"duration {dur:.3f}")
        lines.append(f"file 'f{n - 1:05d}.jpg'")  # concat demuxer wants the last file repeated
        with open(os.path.join(out_dir, "frames.txt"), "w") as fh:
            fh.write("\n".join(lines) + "\n")
        return n, self.frames[-1][0] - self.frames[0][0]

    # ---------- navigation / interaction ----------
    def goto(self, url, settle=1.0):
        self.send("Page.navigate", url=url)
        self.pump(settle)

    def js(self, expr, settle=0.2):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        self.pump(settle)
        return r.get("result", {}).get("value")

    def click_text(self, text, tag="button,a,li,span,td", settle=0.8):
        safe = text.replace("'", "\\'")
        ok = self.js(
            f"(function(){{const els=[...document.querySelectorAll('{tag}')];"
            f"const el=els.find(e=>e.textContent.trim().includes('{safe}'));"
            f"if(!el)return false;el.scrollIntoView({{block:'center'}});el.click();return true;}})()",
            settle,
        )
        return ok

    def type_into(self, selector, text, settle=0.35):
        # clear first so we don't append to prefilled defaults (e.g. depth 2, pages 50)
        self.js(
            f"(function(){{const el=document.querySelector('{selector}');el.focus();el.value='';"
            f"el.dispatchEvent(new Event('input',{{bubbles:true}}));}})()",
            0.1,
        )
        for ch in text:
            self.send("Input.dispatchKeyEvent", type="char", text=ch)
            self.pump(0.11)
        self.pump(settle)

    def set_select(self, selector, value, settle=0.3):
        self.js(
            f"(function(){{const s=document.querySelector('{selector}');"
            f"s.value='{value}';s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()",
            settle,
        )

    def highlight(self, selector, color="#ffd54f", settle=0.9):
        self.js(
            f"(function(){{const e=document.querySelector('{selector}');if(!e)return;"
            f"e.style.outline='4px solid {color}';e.style.outlineOffset='2px';"
            f"e.style.transition='outline 0.2s';e.scrollIntoView({{block:'center'}});}})()",
            settle,
        )

    def clear_highlights(self):
        self.js("[...document.querySelectorAll('*')].forEach(e=>e.style.outline='')", 0.1)

    def banner(self, text, secs=1.6, color="#7c3aed"):
        self.js(
            "(function(t,c){let b=document.getElementById('cdp-banner');"
            "if(!b){b=document.createElement('div');b.id='cdp-banner';document.body.appendChild(b);}"
            "b.textContent=t;b.style.cssText='position:fixed;left:0;right:0;top:0;z-index:999999;"
            "background:'+c+';color:#fff;font:600 17px system-ui;padding:10px 16px;text-align:center;"
            "box-shadow:0 2px 12px rgba(0,0,0,.3)';})("
            + json.dumps(text) + "," + json.dumps(color) + ")",
            0.2,
        )
        self.pump(secs)

    def hold(self, secs):
        self.pump(secs)
