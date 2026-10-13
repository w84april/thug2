"""Serve only the private preview's exact inputs over loopback; no originals.

The executable is absent. Native comparison references are used only by the verification checker; they are never injected as engine inputs.
"""
import json,mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
folder=Path(__file__).resolve().parent
runtime=json.loads((folder/'training-webgl-v1-runtime.json').read_text())
hawk=json.loads((folder/'skater-hawk-webgl-v1-runtime.json').read_text())
names=['training-warehouse-hawk-movement-v9.html','training-warehouse-v2-view.json','training-webgl-v1-runtime.json','training-webgl-v1-storage-proof-v2.json','training-webgl-v1-load.mjs','training-warehouse-hawk-movement-v9-render.mjs',runtime['memory'],runtime['wasm'],runtime['ports'],'skater-hawk-webgl-v1-runtime.json','skater-hawk-webgl-v1-storage-proof.json','skater-hawk-webgl-v2-load.mjs',hawk['memory'],hawk['wasm'],hawk['ports']]
board=json.loads((folder/'skater-board-webgl-v1-runtime.json').read_text())
names+=['skater-board-webgl-v1-runtime.json','skater-board-webgl-v1-storage-proof.json','skater-board-preview-v1-node.json','skinned-model-webgl-v1-load.mjs']+list(board['input_sha256'])
pose=json.loads((folder/'skater-animation-preview-v1-inputs.json').read_text())
names+=['skater-animation-sample-v1.wasm','skater-animation-preview-v1-pose.mjs','skater-animation-preview-v1-inputs.json','skater-animation-preview-v1-matrix-proof.json','skater-animation-preview-v1-node.json']+[v['file'] for v in pose['inputs'].values()]
names+=['skater-browser-motion-v1.mjs','warehouse-shared-collision-v2.mjs','warehouse-skater-traversal-v3.mjs','warehouse-native-ground-traversal-v1-checks.mjs','warehouse-native-ground-traversal-v1-node.json','warehouse-native-ground-traversal-v2-original.json','skater-browser-motion-v1-inputs.json','skater-shared-ground-v1-inputs.json','browser_input.mjs']
for name in ['skater-browser-motion-v1-inputs.json','skater-shared-ground-v1-inputs.json']:names+=list(json.loads((folder/name).read_text())['input_sha256'])
names+=['warehouse-original-physics-jump-traversal-v4.mjs','skater-jump-action-bootstrap-v6.mjs','skater-grounded-air-valid-bootstrap-v2-checks.mjs','skater-jump-action-live-v3-original.json','skater-level-trigger-jump-v1-node.json','skater-jump-action-bootstrap-v6-inputs.json']
names+=list(json.loads((folder/'skater-jump-action-bootstrap-v6-inputs.json').read_text())['input_sha256'])
names+=['skater-jump-action-bootstrap-v6-checks.mjs']
names+=['skater-level-trigger-browser-v1.html','skater-level-trigger-browser-v1-worker.mjs','skater-goal-active-v1-checks.mjs','skater-goal-active-v1-original.json','skater-goal-active-v1-node.json','skater-jump-action-live-v4-original.json','skater-level-trigger-air-release-v1-node.json','skater-level-trigger-route-v1-original.json','skater-level-trigger-route-v1-checks.mjs']
assert all(Path(n).name==n and n.endswith(('.html','.json','.mjs','.bin','.wasm')) for n in names)
validation=folder.parent.parent/'local/validation/collision'
files={'/'+n:(folder/n if (folder/n).exists() else validation/n) for n in names};files['/browser_input.mjs']=folder.parent.parent/'src/platform/browser_input.mjs';files['/']=folder/'training-warehouse-hawk-movement-v9.html';files['/trigger-proof']=folder/'skater-level-trigger-browser-v1.html'
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  path=files.get(urlsplit(self.path).path)
  if path is None:self.send_error(404);return
  data=path.read_bytes();self.send_response(200);self.send_header('Content-Type','text/javascript' if path.suffix=='.mjs' else mimetypes.guess_type(path.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print('Private Warehouse geometry preview: http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
server.serve_forever()
