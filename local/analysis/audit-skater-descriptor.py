"""Read-only audit of descriptor correction and its preserved checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'skater-descriptor-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint'])
assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']=='4435a69384b0741f1958938317c7384ad6a2a76e5b46b391215911c232ec667b'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
for name,digest in c['draft_source_hashes'].items():assert sha(r/name)==digest,name
assert sha(r/c['wasm'])==c['wasm_sha256']
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert sha(r/'progress/report.json')==c['public_report_sha256']=='bc9536003ee770ee309979d754c530cd0f5ff268f2b2722e25271746d0bf24bb'
assert c['new_functions']==0 and c['original_addresses']==[]
assert len(c['verified_scoped_addresses_from_prior'])==15 and c['verified_scoped_addresses_from_prior']==prior['original_addresses']
assert (c['browser_suites'],c['preserved_browser_suites'],c['new_cases'],c['new_completed_calls'])==(189,188,216,432)
assert c['constructor_prefix']==prior['constructor_prefix'] and not c['constructor_prefix']['counted_complete'] and not c['playable']
proof=read(p/'skater-descriptor-browser.json');old=read(p/'skater-end-run-browser.json')['observed']['suites'];observed=proof['observed']['suites'];assert len(observed)==189
assert proof['status'].startswith('PASS') and proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint']
for name,value in observed.items():
 assert value['result']=='pass',name
 if name in old:assert value==old[name],name
negative=read(p/'skater-base-descriptor-negative.json');assert negative['result']=='pass' and negative['incorrect_virtual_rejected']
report={'result':'pass','checkpoint_sha256':sha(path),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'harnesses':len(c['harness_hashes']),'maintained_sources':len(c['source_hashes']),'new_routines':0,'preserved_scoped_routines':15,'descriptor_cases':216,'descriptor_calls':432,'browser_suites':189,'preserved_browser_suites':188,'wrong_virtual_rejected':True,'numeric_allowances':0,'checker_changes':0,'constructor':'293/463 partial','main_wasm_unchanged':True,'public_report_unchanged':True,'publishing_paused':True,'playable':False}
target=p/'skater-descriptor-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
