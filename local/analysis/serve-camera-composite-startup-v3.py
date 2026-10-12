"""Loopback-only, allowlisted development verification server."""
import json,mimetypes,re
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
root=Path.cwd();folder=root/'local/analysis'
files={'/ground-frame-checks.mjs':folder/'walk-ground-frame-checks.mjs','/speed-checks.mjs':folder/'walk-speed-checks.mjs','/ledge-checks.mjs':folder/'walk-ledge-checks.mjs','/walk-checks.mjs':folder/'skater-walk-checks.mjs','/cleanup-checks.mjs':folder/'skater-cleanup-checks.mjs','/gap-end-checks.mjs':folder/'gap-end-checks.mjs','/score-insert-checks.mjs':folder/'score-insert-checks.mjs','/skater-rotate-checks.mjs':folder/'skater-rotate-checks.mjs','/skater-matrix-checks.mjs':folder/'skater-matrix-checks.mjs','/model-initialize-prefix-checks.mjs':folder/'model-initialize-prefix-checks.mjs','/input-command-checks.mjs':folder/'input-command-checks.mjs','/tools/script_state_wasm_checks.mjs':root/'tools/script_state_wasm_checks.mjs','/training-texture-checks.mjs':folder/'lock-frame-training-checks.mjs','/':folder/'camera-composite-startup-v3-browser.html',
 '/worker.mjs':folder/'camera-composite-startup-v3-worker.mjs',
 '/checks.mjs':root/'tools/script_state_wasm_checks.mjs',
 '/setup-checks.mjs':folder/'training-setup-checks.mjs',
 '/prop-script-checks.mjs':folder/'training-prop-script-checks.mjs',
 '/model-checks.mjs':folder/'training-model-component-checks.mjs',
 '/prefix-checks.mjs':folder/'model-initialize-prefix-checks.mjs',
 '/module.wasm':folder/'camera-composite-startup-v2.wasm'}
for name in ["camera-composite-startup-v3", "skater-camera-initialization-v3", "skater-camera-factories-v1", "skater-camera-reset-v1", "animation-state-storage-v3", "animation-component-storage-v3", "camera-viewport-v1", "camera-startup-v2", "skater-initialization-links-v1", "skater-tag-texture", "skater-final-startup", "skater-full-startup", "skater-startup-tail", "skater-startup-tail-parent", "walk-component-frame", "walk-hang-pose", "walk-hang-motion", "walk-hang-exit", "walk-hang-frame", "walk-complete-update", "walk-exit-floor", "walk-rail-frame", "walk-rail-update", "walk-air-frame", "walk-air-update", "walk-air-jump-clearance", "walk-air-contact-jump", "walk-air-rail", "walk-air-landing", "walk-air-wallplant", "walk-air-ledge", "walk-air-plane", "walk-air-transfer", "walk-air-steering", "walk-air-ceiling", "walk-transfer", "walk-ground-validation", "walk-ground-frame", "walk-frame-speed", "walk-frame-speed-flow", "walk-speed", "walk-tail", "walk-camera", "walk-critical", "walk-common", "walk-animation", "walk-grounded", "walk-grab", "walk-floor", "walk-ledge", "walk-transition", "walk-ground", "skater-walk", "skater-cleanup", "skater-finalize", "trigger", "gap-end", "score-insert", "gap-links", "gap-start", "gap-score", "asset-factory", "asset-ready", "composite-construction", "composite-math", "contact-assembly", "contact-assembly-training", "geometry-clone", "input-callbacks", "input-command", "input-lifecycle", "input-pad", "level-collision-component", "level-collision-component-unit", "level-collision-load", "level-collision-load-unit", "level-material", "level-mesh", "level-object-startup", "level-register", "level-sector", "lock-frame", "lock-frame-training", "material-buffer", "mesh-index", "mesh-register", "model-asset", "model-component", "model-configuration", "model-configuration-prefix", "model-initialize", "model-initialize-prefix", "model-transform", "motion-frame", "motion-frame-training", "motion-rotation", "motion-rotation-training", "node-index", "node-prefix", "node-registration", "particle-command", "particle-component", "particle-component-training", "particle-create", "particle-create-training", "particle-dispatch", "particle-dispatch-training", "particle-emission", "particle-engine", "particle-engine-training", "particle-frame", "particle-image", "particle-image-training", "particle-setup", "particle-setup-training", "particle-simulation", "particle-startup", "particle-update", "prop-command", "prop-lifecycle", "prop-sound", "proximity-frame", "proximity-frame-training", "render-instance", "renderer-bounds", "rigidbody-core", "rigidbody-initialize", "rigidbody-initialize-training", "rigidbody-kick", "rigidbody-motion", "rigidbody-response", "rigidbody-solver", "rigidbody-update", "rigidbody-update-active-training", "rigidbody-update-training", "scene-construction", "scene-create", "scene-disposal", "scene-finalize", "scene-kill", "scene-lifetime", "scene-name", "scene-proximity", "scene-state", "scene-subscribe", "scene-visitor", "script-change", "skater-adjust", "skater-construction", "skater-gap", "skater-ground", "skater-matrix", "skater-rotate", "skater-score", "skater-score-assets", "skater-trick", "skeleton-asset", "skeleton-buffer", "sphere-contact", "sphere-contact-training", "sphere-geometry", "sphere-geometry-training", "sphere-query", "sphere-query-training", "sphere-sweep", "sphere-sweep-training", "texture-asset", "texture-buffer", "training-asset-ready", "training-geometry-clone", "training-geometry-clone-shared", "training-level-material", "training-level-mesh", "training-level-register", "training-level-register-shared", "training-level-sector", "training-load", "training-material-buffer", "training-mesh-index", "training-mesh-register", "training-mode", "training-model-component", "training-model-configuration", "training-model-file", "training-model-initialize", "training-model-transform", "training-node-index", "training-node-registration", "training-prop-components", "training-prop-script", "training-render-instance", "training-renderer-bounds", "training-scene-construction", "training-scene-create", "training-scene-finalize", "training-setup", "training-texture-asset", "training-vertex-upload", "vertex-upload", "skater-base-descriptor", "skater-local-net", "skater-end-run-lifecycle", "skater-end-run-startup", "skater-balance-lifecycle", "skater-balance-startup", "skater-looping-sound-lifecycle", "skater-looping-sound-startup"]:
 path=folder/(name+'-fixtures.json');files['/'+path.name]=path
 # Only dependency filenames are needed here; the browser parses full fixtures.
 # Current exporters place them in leading/trailing metadata. Missing entries
 # cause strict browser fetch failures, never weaker comparisons.
 with path.open('rb') as stream:
  head=stream.read(1048576);stream.seek(max(0,path.stat().st_size-1048576));tail=stream.read()
 names=set(re.findall(rb'"(?:memory|memory_fixture|module)"\s*:\s*"([^"\\]+)"',head+tail))
 assert any(n.endswith(b'.bin') for n in names),name
 names={n.decode('utf-8') for n in names}
 assert all(Path(n).name==n and Path(n).suffix in {'.bin','.wasm'} for n in names),names
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
