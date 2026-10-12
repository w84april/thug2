"""Loopback-only, allowlisted development verification server."""
import json,mimetypes
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
root=Path.cwd();folder=root/'local/analysis'
files={'/walk-checks.mjs':folder/'skater-walk-checks.mjs','/cleanup-checks.mjs':folder/'skater-cleanup-checks.mjs','/gap-end-checks.mjs':folder/'gap-end-checks.mjs','/score-insert-checks.mjs':folder/'score-insert-checks.mjs','/skater-rotate-checks.mjs':folder/'skater-rotate-checks.mjs','/skater-matrix-checks.mjs':folder/'skater-matrix-checks.mjs','/model-initialize-prefix-checks.mjs':folder/'model-initialize-prefix-checks.mjs','/input-command-checks.mjs':folder/'input-command-checks.mjs','/tools/script_state_wasm_checks.mjs':root/'tools/script_state_wasm_checks.mjs','/training-texture-checks.mjs':folder/'lock-frame-training-checks.mjs','/':folder/'walk-ground-browser.html',
 '/worker.mjs':folder/'walk-ground-worker.mjs',
 '/checks.mjs':root/'tools/script_state_wasm_checks.mjs',
 '/setup-checks.mjs':folder/'training-setup-checks.mjs',
 '/prop-script-checks.mjs':folder/'training-prop-script-checks.mjs',
 '/model-checks.mjs':folder/'training-model-component-checks.mjs',
 '/prefix-checks.mjs':folder/'model-initialize-prefix-checks.mjs',
 '/module.wasm':folder/'walk-ground-draft.wasm'}
for name in ['walk-ground','skater-walk','skater-cleanup','skater-finalize','trigger','gap-end','score-insert','gap-links','gap-start','gap-score','skater-ground','skater-adjust','skater-gap','skater-rotate','skater-trick','skater-matrix','skater-score','skater-score-assets','skater-construction','input-command','input-lifecycle','input-callbacks','input-pad','rigidbody-update','rigidbody-update-training','rigidbody-update-active-training','rigidbody-kick','contact-assembly','contact-assembly-training','sphere-query','sphere-query-training','sphere-contact','sphere-contact-training','sphere-sweep','sphere-sweep-training','sphere-geometry','sphere-geometry-training','rigidbody-solver','motion-rotation','motion-rotation-training','rigidbody-response','particle-dispatch','particle-dispatch-training','particle-update','particle-simulation','particle-emission','particle-command','particle-frame','lock-frame','lock-frame-training','proximity-frame','proximity-frame-training','motion-frame','motion-frame-training','particle-setup','particle-setup-training','particle-image','particle-image-training','particle-create','particle-create-training','particle-engine','particle-engine-training','particle-component','particle-component-training','particle-startup','rigidbody-motion','rigidbody-initialize','rigidbody-initialize-training','rigidbody-core','level-collision-component','level-collision-component-unit','level-collision-load','level-collision-load-unit','level-object-startup','geometry-clone','training-geometry-clone','training-geometry-clone-shared','level-register','training-level-register','training-level-register-shared','level-sector','training-level-sector','level-mesh','training-level-mesh','level-material','training-level-material','scene-create','training-scene-create','model-transform','training-model-transform','renderer-bounds','training-renderer-bounds','render-instance','training-render-instance','asset-ready','training-asset-ready','scene-finalize','training-scene-finalize','mesh-register','training-mesh-register','vertex-upload','training-vertex-upload','mesh-index','training-mesh-index','scene-construction','training-scene-construction','material-buffer','training-material-buffer','model-asset','training-model-file','texture-asset','training-texture-asset','texture-buffer','model-configuration','model-configuration-prefix','training-model-configuration','model-initialize','model-initialize-prefix','training-model-initialize','model-component','training-model-component','prop-command','training-prop-script','prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']:
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
print('Training scene verification: http://127.0.0.1:'+str(server.server_port)+'/',flush=True)
server.serve_forever()
