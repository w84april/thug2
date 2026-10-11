"""Loopback-only allowlisted server for the isolated command comparison page."""
import json,mimetypes
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
root=Path.cwd();folder=root/'local/analysis'
files={'/':folder/'physics-command-values-browser.html',
 '/worker.mjs':folder/'physics-commands-worker.mjs',
 '/checks.mjs':root/'tools/script_state_wasm_checks.mjs',
 '/module.wasm':folder/'physics-movement-members-draft.wasm'}
for name in ['physics-parameter-flags','physics-airtime','physics-script-outputs','physics-movement-members','physics-command-values-context']:
 path=folder/(name+'-fixtures.json');files['/'+path.name]=path
 fixture=json.loads(path.read_text());names={fixture['memory']}
 if fixture.get('memory_fixture'):names.add(fixture['memory_fixture'])
 names.update(row['module'] for row in fixture.get('native_callbacks',[]))
 for filename in names:
  path=folder/filename
  if not path.exists():path=root/'local/validation/collision'/filename
  assert path.is_file(),filename
  files['/'+filename]=path
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  path=files.get(urlsplit(self.path).path)
  if path is None:self.send_error(404);return
  data=path.read_bytes();self.send_response(200)
  self.send_header('Content-Type','text/javascript' if path.suffix=='.mjs' else mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
  self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print('Physics command validation: http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
server.serve_forever()
