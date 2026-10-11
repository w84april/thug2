"""Original scene/wall-mark behavior, tested through its recovered callees."""
import hashlib,json,subprocess
from specimen import ROOT,SHA256
from wall_marks_fixtures import build_wall_marks
out=ROOT/'local/validation/collision';report_path=out.parent/'wall-marks.json'
report_path.unlink(missing_ok=True)
fixture,path,oracle=build_wall_marks(out)
subprocess.run(['node',str(ROOT/'tools/verify_wall_marks_wasm.mjs'),str(out)],check=True)
artifacts=[path,*[out/name for name in [fixture['memory'],'decal-projection-callbacks.wasm','script-values-memory.wasm']]]
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),
 'zeroed_packet_padding_entries':fixture['zeroed_packet_padding_entries'],'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':fixture['scope'],
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS wall marks',flush=True)
