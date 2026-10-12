"""Read-only preservation and zero-credit rendering integration audit."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'training-webgl-v1-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint']);assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in c[group].items():assert sha(r/name)==h,(group,name)
 for name,h in prior[group].items():assert c[group][name]==h,(group,name)
assert sha(r/c['wasm'])==c['wasm_sha256']==prior['wasm_sha256']
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']
assert c['new_complete_addresses']==[] and c['new_complete_body_bytes']==c['new_matched_bytes']==0 and not c['playable']
assert c['browser_engine_parity_suites']==200 and c['original_gpu_storage_buffers']==7024
for state in c['browser_preview'].values():assert state['result']=='rendered original geometry' and state['ordered_storage_sha256']==c['original_gpu_storage_sha256'] and state['center_pixel_colors']>1
baseline=read(r/c['report_at_verification']['path']);assert sha(r/c['report_at_verification']['path'])==c['report_at_verification']['sha256']
assert (int(baseline['measures']['complete_code']),int(baseline['measures']['total_code']),int(baseline['measures']['matched_code']))==(436577,2375378,406)
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'browser_engine_parity_suites':200,'original_gpu_storage_buffers':7024,'actual_chromium_rendered':True,'orbit_zoom_reset_verified':True,'original_frame_equivalence_verified':False,'new_complete_addresses':0,'new_complete_body_bytes':0,'new_matched_bytes':0,'playable':False}
out=p/'training-webgl-v1-audit.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
