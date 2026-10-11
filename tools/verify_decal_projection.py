"""Complete mesh cleanup and surface-mark projection, original and Wasm."""
import hashlib,json,subprocess
from specimen import ROOT,SHA256
from mesh_lifecycle_fixtures import build_lifecycle
from decal_projection_fixtures import build_projection
out=ROOT/'local/validation/collision';report_path=out.parent/'decal-projection.json'
report_path.unlink(missing_ok=True)
lifecycle,lifecycle_path,lifecycle_oracle,callbacks=build_lifecycle(out)
projection,projection_path,projection_oracle=build_projection(out)
subprocess.run(['node',str(ROOT/'tools/verify_decal_projection_wasm.mjs'),str(out)],check=True)
artifacts=[lifecycle_path,projection_path,*[out/name for name in [lifecycle['memory'],projection['memory'],'mesh-lifecycle-callbacks.wasm','decal-projection-callbacks.wasm','script-values-memory.wasm']]]
report={'result':'pass','specimen_sha256':SHA256,
 'lifecycle_counts':dict(lifecycle_oracle.counts),'lifecycle_callee_coverage':dict(lifecycle_oracle.coverage),'lifecycle_external_callbacks':callbacks,
 'projection_counts':dict(projection_oracle.counts),'projection_callee_coverage':dict(projection_oracle.coverage),
 'heap_events':{'lifecycle':dict(lifecycle_oracle.heap_events),'projection':dict(projection_oracle.heap_events)},
 'scope':lifecycle['scope']+' '+projection['scope'],
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS complete decal projection',flush=True)
