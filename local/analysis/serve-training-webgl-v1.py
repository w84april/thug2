"""Serve only the private preview's exact inputs over loopback; no originals.

The original executable and output snapshots are deliberately absent.
"""
import json,mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
folder=Path(__file__).resolve().parent
runtime=json.loads((folder/'training-webgl-v1-runtime.json').read_text())
names=['training-webgl-v1.html','training-webgl-v1-runtime.json','training-webgl-v1-storage-proof-v2.json','training-webgl-v1-load.mjs','training-webgl-v1-render.mjs',runtime['memory'],runtime['wasm'],runtime['ports']]
assert all(Path(n).name==n and n.endswith(('.html','.json','.mjs','.bin','.wasm')) for n in names)
files={'/'+n:folder/n for n in names};files['/']=folder/'training-webgl-v1.html'
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  path=files.get(urlsplit(self.path).path)
  if path is None:self.send_error(404);return
  data=path.read_bytes();self.send_response(200);self.send_header('Content-Type','text/javascript' if path.suffix=='.mjs' else mimetypes.guess_type(path.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print('Private training rendering preview: http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
server.serve_forever()
