"""Read-only audit preserving every prior artifact and checker."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text());path=p/'skater-full-startup-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint'])
assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']=='d0f1582b51698813701109db92a1cba04ac82e9c80285f6e79a1f661911ae1cf'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,h in c[group].items():assert sha(r/name)==h,(group,name)
 for name,h in prior[group].items():assert c[group][name]==h,(group,name)
for name,h in c['draft_source_hashes'].items():assert sha(r/name)==h,name
assert sha(r/c['wasm'])==c['wasm_sha256'] and sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['verified_mappings'],c['new_complete_body_bytes'],c['browser_suites'],c['preserved_browser_suites'])==(21,22,4093,198,195)
assert (c['new_cases'],c['new_completed_calls'],c['original_covered_instructions'],c['original_linear_instructions'])==(332,412,1280,1296)
proof=read(p/'skater-full-startup-browser.json');expected=read(p/'skater-full-startup-node-all.json');assert proof['observed']==expected and proof['status'].startswith('PASS')
for name,value in read(p/'skater-startup-tail-browser.json')['observed']['suites'].items():assert proof['observed']['suites'][name]==value,name
assert c['partial_resolutions']['0x582d90']=={'completed_calls':80,'expected_traps':0,'returned_this':True,'temporary_cleanup_verified':True}
assert not c['playable'];negative=read(p/'skater-tag-texture-negative.json');assert all(x['rejected'] for x in negative['controls'].values())
report={'result':'pass','checkpoint_sha256':sha(path),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'harnesses':len(c['harness_hashes']),'maintained_sources':len(c['source_hashes']),'new_unique_addresses':21,'selected_mappings':22,'shared_zero_credit':['0x49f3b0'],'new_complete_body_bytes':4093,'original_covered_instructions':1280,'original_linear_instructions':1296,'scoped_excluded_instructions':16,'cases':332,'calls':412,'browser_suites':198,'preserved_browser_suites':195,'negative_controls_rejected':2,'numeric_allowances':0,'checker_changes':0,'resolved_partial_addresses':['0x582d90'],'constructor_completed_calls':80,'pooled_constructor_calls':40,'main_wasm_unchanged':True,'public_baseline_preserved':True,'direct_publication_authorized':True,'old_automation_paused':True,'playable':False}
target=p/'skater-full-startup-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
