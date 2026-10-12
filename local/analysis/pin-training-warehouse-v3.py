"""Pin the scene identity correction and zero-credit Warehouse preview."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
previous=p/'animation-component-storage-v3-checkpoint.json';prior=read(previous)
assert sha(previous)=='4539ac1e1bf455980713e4e51ad56b599c0abf7e6cd8b9ce4dd4196a2ec0e459'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in prior[group].items():assert sha(r/name)==h,(group,name)
verification=read(p/'training-warehouse-v2-view-verification.json');assert verification['result']=='pass' and not verification['playable']
view=read(p/'training-warehouse-v2-view.json');runtime=read(p/'training-webgl-v1-runtime.json')
for name,h in runtime['input_sha256'].items():assert sha(p/name)==h,name
assert verification['complete_engine_suites']==prior['browser_suites']==202
baseline=p/'training-warehouse-v3-reporting-baseline-report.json';assert not baseline.exists();baseline.write_bytes((r/'progress/report.json').read_bytes())
report=read(baseline);assert tuple(int(report['measures'][k]) for k in ['complete_code','total_code','matched_code'])==(437104,2375378,406)
paths={previous,p/'animation-component-storage-v3-audit.json',baseline,r/'local/build/training-warehouse-v2-audit-failed.log',p/'pin-training-warehouse-v3.py',p/'audit-training-warehouse-v3.py'}
for pattern in ['inspect-tr-scene-identity-v*','tr-scene-identity-v*','inspect-tr-level-selection-v1*','tr-level-selection-v1*','inspect-tr-warehouse-geometry-v1*','tr-warehouse-geometry-v1*','tr-warehouse-v2*','tr-warehouse-v1-gameplay-reference.jpg','training-warehouse-v*','prepare-training-warehouse-v*','serve-training-warehouse-v*','check-training-warehouse-v2*','pin-training-warehouse-v2*','audit-training-warehouse-v2*','animation-component-storage-v3-report-validation.log','animation-component-storage-v3-report-generation.log','animation-component-storage-v3-reconciliation*.log','animation-initialization-v3-discovery.json']:
 paths.update(f for f in p.glob(pattern) if f.is_file())
paths.update(r/name for name in view['original_scene_assets'])
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 artifacts[str(f.relative_to(r))]=sha(f)
 if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
observed={name:read(p/('training-warehouse-v2-browser-'+name+'.json')) for name in ['initial','zoom','orbit','overview','reset']}
c={'schema':2,'result':'original TR identity audited; actual Chromium Warehouse geometry preview passes; zero recovery credit','prior_checkpoint':str(previous.relative_to(r)),'prior_checkpoint_sha256':sha(previous),'specimen_sha256':prior['specimen_sha256'],'artifact_hashes':dict(sorted(artifacts.items())),'source_hashes':prior['source_hashes'],'platform_source_hashes':prior['platform_source_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'harness_hashes':dict(sorted(harnesses.items())),'preserved_artifacts':len(prior['artifact_hashes']),'wasm':prior['wasm'],'wasm_sha256':prior['wasm_sha256'],'main_wasm_sha256':prior['main_wasm_sha256'],'browser_engine_parity_suites':202,'preview_engine_wasm':str((p/runtime['wasm']).relative_to(r)),'preview_engine_wasm_sha256':sha(p/runtime['wasm']),'view_metadata_sha256':sha(p/'training-warehouse-v2-view.json'),'original_gpu_storage_buffers':7024,'original_gpu_storage_sha256':view['original_storage_sha256'],'browser_preview':observed,'scene_identity_verification':verification,'screenshot':'local/analysis/training-warehouse-v2-verified.jpg','report_at_verification':{'path':str(baseline.relative_to(r)),'sha256':sha(baseline)},'new_complete_addresses':[],'new_complete_body_bytes':0,'new_matched_bytes':0,'preserved_failed_pin':'local/analysis/training-warehouse-v2-checkpoint.json','preserved_failed_pin_reason':'The v2 pin included its own changing runner log; its preservation audit rejected that digest. v3 keeps the failed pin and final log as evidence and runs with logs outside the selected input patterns. No engine or rendering comparator changed.','scope':view['view_scope']+' '+view['selection'],'original_default_gameplay_spawn_verified':False,'original_gameplay_camera_verified':False,'original_visibility_transforms_frame_equivalence_verified':False,'playable':False}
t=p/'training-warehouse-v3-checkpoint.json';assert not t.exists();t.write_text(json.dumps(c,indent=2)+'\n');print('Pinned',len(artifacts),'artifacts, preserving',len(prior['artifact_hashes']),'with zero new recovery credit;',sha(t))
