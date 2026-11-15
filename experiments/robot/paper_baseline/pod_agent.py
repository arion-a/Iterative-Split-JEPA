"""Tiny authenticated file/exec server that runs inside the GPU pod (stdlib only). Header X-Token must match $AGENT_TOKEN."""
import hmac, json, os, subprocess, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
TOKEN = os.environ["AGENT_TOKEN"]; ROOT = "/workspace"; os.makedirs(ROOT, exist_ok=True)
def safe(p): full = os.path.realpath(os.path.join(ROOT, p.lstrip("/"))); assert full.startswith(ROOT), "outside workspace"; return full
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def ok(self): return hmac.compare_digest(self.headers.get("X-Token", ""), TOKEN)
    def send(self, code, body=b"", ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def q(self): u = urllib.parse.urlparse(self.path); return u.path, {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
    def do_PUT(self):
        if not self.ok(): return self.send(403)
        _, a = self.q(); p = safe(a["path"]); os.makedirs(os.path.dirname(p), exist_ok=True); n = int(self.headers["Content-Length"]); data = self.rfile.read(n)
        mode = "r+b" if os.path.exists(p) else "wb"
        with open(p, mode) as f: f.seek(int(a.get("offset", 0))); f.write(data)
        self.send(200, json.dumps({"written": n}).encode())
    def do_POST(self):
        if not self.ok(): return self.send(403)
        path, _ = self.q(); body = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or b"{}")
        if path == "/exec":
            log = safe(body.get("log", "logs/last.log")); os.makedirs(os.path.dirname(log), exist_ok=True)
            if body.get("bg"):
                subprocess.Popen(["bash", "-lc", body["cmd"]], cwd=ROOT, stdout=open(log, "ab"), stderr=subprocess.STDOUT, start_new_session=True); return self.send(200, b'{"started":true}')
            r = subprocess.run(["bash", "-lc", body["cmd"]], cwd=ROOT, capture_output=True, text=True, timeout=int(body.get("timeout", 80)))
            return self.send(200, json.dumps({"rc": r.returncode, "out": (r.stdout + r.stderr)[-20000:]}).encode())
        self.send(404)
    def do_GET(self):
        if not self.ok(): return self.send(403)
        path, a = self.q()
        if path == "/tail":
            p = safe(a["path"]); n = int(a.get("n", 4000)); data = open(p, "rb").read()[-n:] if os.path.exists(p) else b""; return self.send(200, data, "text/plain")
        if path == "/download":
            p = safe(a["path"]); off, ln = int(a.get("offset", 0)), int(a.get("length", 32 << 20))
            with open(p, "rb") as f: f.seek(off); return self.send(200, f.read(ln), "application/octet-stream")
        if path == "/size": p = safe(a["path"]); return self.send(200, json.dumps({"size": os.path.getsize(p) if os.path.exists(p) else -1}).encode())
        self.send(200, b'{"ok":true}')
ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
