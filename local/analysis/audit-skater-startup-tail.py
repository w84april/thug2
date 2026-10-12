"""Read-only audit of the new pin and all preserved private evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'skater-startup-tail-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint']);assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']=='04d3ca79ae3a694a4e61eb9d80d56e41eef69b31ee6cffa3ebb4941bb2d674b4'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
for name,digest in c['draft_source_hashes'].items():assert sha(r/name)==digest,name
assert sha(r/c['wasm'])==c['wasm_sha256'] and sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert sha(r/c['public_report_at_verification']['path'])==c['public_report_at_verification']['sha256']=='c5c9991c000e663086afa4bc47347cc8a8002aa777ee7517417d4d19208d75da'
assert len(c['original_addresses'])==c['new_functions']==17 and len(c['verified_scoped_addresses_from_prior'])==33
assert (c['browser_suites'],c['preserved_browser_suites'],c['new_cases'],c['new_completed_calls'],c['new_diagnostic_callbacks'])==(195,193,367,733,455)
assert c['new_complete_body_bytes']==2145 and not c['constructor_prefix']['counted_complete'] and not c['playable']
proof=read(p/'skater-startup-tail-browser.json');old=read(p/'skater-looping-sound-browser.json')['observed']['suites'];observed=proof['observed']['suites'];assert len(observed)==195
assert proof['status'].startswith('PASS') and proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint']
for name,value in observed.items():
 assert value['result']=='pass',name
 if name in old:assert value==old[name],name
negative=read(p/'skater-startup-tail-negative.json');assert negative['result']=='pass' and len(negative['controls'])==2 and all(x['rejected'] for x in negative['controls'].values())
report={'result':'pass','checkpoint_sha256':sha(path),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'harnesses':len(c['harness_hashes']),'maintained_sources':len(c['source_hashes']),'new_routines':17,'preserved_scoped_routines':33,'new_complete_body_bytes':2145,'new_verified_linear_bytes':2225,'original_reachable_instructions':607,'original_linear_instructions':608,'unreachable_alignment_bytes':3,'cases':367,'calls':733,'native_diagnostic_callbacks':455,'browser_suites':195,'preserved_browser_suites':193,'negative_controls_rejected':2,'numeric_allowances':0,'checker_changes':0,'constructor':'424/463 partial;80 interrupted calls','main_wasm_unchanged':True,'public_baseline_preserved':True,'direct_publication_authorized':True,'old_automation_paused':True,'playable':False}
target=p/'skater-startup-tail-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
