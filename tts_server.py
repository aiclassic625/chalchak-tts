#!/usr/bin/env python3
"""Free Edge neural TTS cache server for 찰칵중국어 (local prototype)."""
import asyncio, hashlib, os, sys, tempfile
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import edge_tts

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE, exist_ok=True)
VOICES = {
    "female": "zh-CN-XiaoxiaoNeural",
    "male": "zh-CN-YunxiNeural",
    "female2": "zh-CN-XiaoyiNeural",
    "male2": "zh-CN-YunjianNeural",
}
MAX = 500

def synth(text, voice, out):
    async def run():
        comm = edge_tts.Communicate(text, voice, rate="-8%", pitch="+0Hz")
        await comm.save(out)
    asyncio.run(run())

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "public, max-age=86400")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            self.send_response(200); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}'); return
        if u.path != "/tts":
            self.send_response(404); self._cors(); self.end_headers(); return
        q = parse_qs(u.query)
        text = (q.get("text") or [""])[0].strip()
        voice_key = (q.get("voice") or ["female"])[0]
        voice = VOICES.get(voice_key, VOICES["female"])
        if not text:
            self.send_response(400); self._cors(); self.end_headers(); self.wfile.write(b"empty text"); return
        text = text[:MAX]
        h = hashlib.sha1((voice + "\n" + text).encode("utf-8")).hexdigest()
        f = os.path.join(CACHE, h + ".mp3")
        if not os.path.exists(f):
            tmp = f + ".tmp"
            try:
                synth(text, voice, tmp)
                os.replace(tmp, f)
            except Exception as e:
                if os.path.exists(tmp): os.unlink(tmp)
                self.send_response(502); self._cors(); self.send_header("Content-Type","text/plain; charset=utf-8"); self.end_headers(); self.wfile.write(("TTS error: " + str(e)[:200]).encode()); return
        data = open(f, "rb").read()
        self.send_response(200); self._cors(); self.send_header("Content-Type", "audio/mpeg"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    port = int(os.environ.get("PORT") or os.environ.get("TTS_PORT") or "8766")
    host = os.environ.get("TTS_HOST", "0.0.0.0")
    print("TTS server on http://%s:%d" % (host, port), flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
