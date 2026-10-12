"""Read-only audit; mutable public reporting is separate from the pinned baseline."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'skater-balance-startup-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint'])
assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']=='c70bc9171a993e557ae353f7feae08721295111f88cf7e2ac8f644aae349df32'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
for name,digest in c['draft_source_hashes'].items():assert sha(r/name)==digest,name
assert sha(r/c['wasm'])==c['wasm_sha256']
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
ref=c['public_report_at_verification'];assert sha(r/ref['path'])==ref['sha256']==prior['public_report_sha256']
assert len(c['original_addresses'])==c['new_functions']==10 and len(c['verified_scoped_addresses_from_prior'])==15
assert (c['browser_suites'],c['preserved_browser_suites'],c['new_cases'],c['new_completed_calls'],c['new_script_callbacks'])==(191,189,115,328,28)
assert not c['constructor_prefix']['counted_complete'] and not c['playable']
proof=read(p/'skater-balance-browser.json');old=read(p/'skater-descriptor-browser.json')['observed']['suites'];observed=proof['observed']['suites'];assert len(observed)==191
assert proof['status'].startswith('PASS') and proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint']
for name,value in observed.items():
 assert value['result']=='pass',name
 if name in old:assert value==old[name],name
negative=read(p/'skater-balance-lifecycle-negative.json');assert negative['result']=='pass' and negative['missing_conditional_qb_rejected']
report={'result':'pass','checkpoint_sha256':sha(path),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'harnesses':len(c['harness_hashes']),'maintained_sources':len(c['source_hashes']),'new_routines':10,'preserved_scoped_routines':15,'original_instructions':185,'cases':115,'calls':328,'native_script_callbacks':28,'browser_suites':191,'preserved_browser_suites':189,'missing_qb_rejected':True,'numeric_allowances':0,'checker_changes':0,'constructor':'301/463 partial','main_wasm_unchanged':True,'public_baseline_preserved':True,'direct_publication_authorized':True,'old_automation_paused':True,'playable':False}
target=p/'skater-balance-startup-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
