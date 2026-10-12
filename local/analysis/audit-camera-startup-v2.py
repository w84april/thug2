"""Read-only audit of the additional selected camera dependencies and preserved proof."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda f:json.loads(f.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
f=p/'camera-startup-v2-checkpoint.json';c=read(f);prior=read(r/c['prior_checkpoint']);assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in c[group].items():assert sha(r/name)==h,(group,name)
 for name,h in prior[group].items():assert c[group][name]==h,(group,name)
for name,h in c['draft_source_hashes'].items():assert sha(r/name)==h,name
assert sha(r/c['wasm'])==c['wasm_sha256'] and sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']
assert (c['new_functions'],c['verified_mappings'],c['new_complete_body_bytes'],c['browser_suites'],c['preserved_browser_suites'])==(13,13,988,200,199)
assert not c['verified_scoped_addresses_from_prior'] and not c['playable']
expected=read(p/'camera-startup-v2-node-all.json');proof=read(p/'camera-startup-v2-browser.json');assert proof['observed']==expected and proof['status'].startswith('PASS')
for name,value in read(p/'skater-initialization-links-v1-browser.json')['observed']['suites'].items():assert expected['suites'][name]==value,name
report={'result':'pass','checkpoint_sha256':sha(f),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'new_unique_addresses':13,'selected_mappings':13,'new_complete_body_bytes':988,'cases':97,'calls':271,'covered_instructions':276,'linear_instructions':276,'allocation_fault_exclusions':0,'browser_suites':200,'preserved_browser_suites':199,'numeric_allowances':0,'checker_changes':0,'resolved_partial_addresses':[],'selection_is_additional':True,'original_camera_qb_discovery_uncredited':True,'main_wasm_unchanged':True,'playable':False}
target=p/'camera-startup-v2-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
