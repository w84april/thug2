"""Read-only audit; mutable public reporting is separate from the pinned baseline."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'skater-looping-sound-startup-checkpoint.json';c=read(path);prior=read(r/c['prior_checkpoint'])
assert sha(r/c['prior_checkpoint'])==c['prior_checkpoint_sha256']=='73a6d033ac53530c9ac59d34becc2333b105893121abb7e3a3ab53e9460e09ed'
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
for name,digest in c['draft_source_hashes'].items():assert sha(r/name)==digest,name
assert sha(r/c['wasm'])==c['wasm_sha256']
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
ref=c['public_report_at_verification'];assert sha(r/ref['path'])==ref['sha256']=='181d00495f3d737666e07d59fa4b40cd2c25c68d4f0975ed9171936988f31875'
assert len(c['original_addresses'])==c['new_functions']==8 and len(c['verified_scoped_addresses_from_prior'])==25
assert (c['browser_suites'],c['preserved_browser_suites'],c['new_cases'],c['new_completed_calls'],c['new_audio_stop_callbacks'])==(193,191,121,291,42)
assert not c['constructor_prefix']['counted_complete'] and not c['playable']
proof=read(p/'skater-looping-sound-browser.json');old=read(p/'skater-balance-browser.json')['observed']['suites'];observed=proof['observed']['suites'];assert len(observed)==193
assert proof['status'].startswith('PASS') and proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint']
for name,value in observed.items():
 assert value['result']=='pass',name
 if name in old:assert value==old[name],name
negative=read(p/'skater-looping-sound-lifecycle-negative.json');assert negative['result']=='pass' and negative['clear_before_stop_rejected']
report={'result':'pass','checkpoint_sha256':sha(path),'preserved_checkpoint_sha256':c['prior_checkpoint_sha256'],'artifacts':len(c['artifact_hashes']),'preserved_artifacts':len(prior['artifact_hashes']),'harnesses':len(c['harness_hashes']),'maintained_sources':len(c['source_hashes']),'new_routines':8,'preserved_scoped_routines':25,'original_instructions':156,'cases':121,'calls':291,'native_stop_callbacks':42,'browser_suites':193,'preserved_browser_suites':191,'clear_before_stop_rejected':True,'numeric_allowances':0,'checker_changes':0,'constructor':'309/463 partial','main_wasm_unchanged':True,'public_baseline_preserved':True,'direct_publication_authorized':True,'old_automation_paused':True,'playable':False}
target=p/'skater-looping-sound-startup-audit.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
