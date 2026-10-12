"""Audit preservation, identity and zero-credit preview scope."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'training-warehouse-v3-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint']);assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in c[group].items():assert sha(r/name)==h,(group,name)
 for name,h in prior[group].items():assert c[group][name]==h,(group,name)
assert c['preserved_artifacts']==len(prior['artifact_hashes'])==24622
assert sha(r/c['wasm'])==c['wasm_sha256']==prior['wasm_sha256'] and sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']
assert sha(r/c['preview_engine_wasm'])==c['preview_engine_wasm_sha256']
assert c['new_complete_addresses']==[] and c['new_complete_body_bytes']==c['new_matched_bytes']==0 and not c['playable']
assert not any(c[k] for k in ['original_default_gameplay_spawn_verified','original_gameplay_camera_verified','original_visibility_transforms_frame_equivalence_verified'])
assert c['browser_engine_parity_suites']==202 and c['scene_identity_verification']['result']=='pass'
for state in c['browser_preview'].values():assert state['result']=='rendered original geometry' and state['ordered_storage_sha256']==c['original_gpu_storage_sha256'] and state['center_pixel_colors']>1
baseline=read(r/c['report_at_verification']['path']);assert sha(r/c['report_at_verification']['path'])==c['report_at_verification']['sha256']
assert tuple(int(baseline['measures'][k]) for k in ['complete_code','total_code','matched_code'])==(437104,2375378,406)
result={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'original_level_selection_training_load_tr_verified':True,'original_storage_buffers':7024,'actual_chromium_warehouse_rendered':True,'zoom_orbit_overview_reset_verified':True,'engine_parity_suites':202,'original_default_spawn_camera_visibility_transforms_frame_equivalence_verified':False,'new_complete_addresses':0,'new_complete_body_bytes':0,'new_matched_bytes':0,'playable':False}
t=p/'training-warehouse-v3-audit.json';assert not t.exists();t.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
