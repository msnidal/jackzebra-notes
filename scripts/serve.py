"""Loopback-only preview; album audio is served locally and excluded from hosting."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import json, os, re, argparse

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT.parent / '.local-media'
MANIFEST = json.loads((MEDIA / 'manifest.json').read_text()) if (MEDIA / 'manifest.json').exists() else {'tracks': []}
TRACKS = {str(t['track']): Path(t['path']) for t in MANIFEST['tracks']}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'dist'), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/__local/manifest':
            payload = json.dumps({'tracks': [{'id': int(n)} for n in TRACKS]}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)
        elif path.startswith('/__local/audio/'):
            track = path.removeprefix('/__local/audio/')
            source = TRACKS.get(track)
            if not source or not source.is_file():
                self.send_error(404)
                return
            size = source.stat().st_size
            start, end = 0, size - 1
            range_header = self.headers.get('Range')
            if range_header:
                match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
                if not match or not any(match.groups()):
                    self.send_error(416)
                    return
                if match[1]:
                    start = int(match[1]); end = min(int(match[2]) if match[2] else size-1, size-1)
                else:
                    start = max(0, size-int(match[2]))
                if start >= size or start > end:
                    self.send_response(416)
                    self.send_header('Content-Range', f'bytes */{size}')
                    self.end_headers()
                    return
            self.send_response(206 if range_header else 200)
            self.send_header('Content-Type', 'audio/flac')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', str(end-start+1))
            if range_header:
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.end_headers()
            try:
                with source.open('rb') as stream:
                    stream.seek(start)
                    remaining = end-start+1
                    while remaining:
                        chunk = stream.read(min(65536, remaining))
                        if not chunk: break
                        self.wfile.write(chunk); remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            super().do_GET()

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=4173)
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1', args.port),Handler)
    print(f'Local: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
