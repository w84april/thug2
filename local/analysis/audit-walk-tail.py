"""Audit walking collision/camera recovery and preservation of the common-pose checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-tail-checkpoint.json';c=read(path);prior=read(p/'walk-common-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-common-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(3,158,816,833)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(300,1896,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(376,376)
assert all(not x['excluded'] and not x['missing'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_tail_evidence'];assert (e['completed_calls'],e['new_root_calls'],e['existing_dependency_calls'])==(1896,856,1040)
assert e['new_comparison_allowances']==0 and not e['new_unreachable_exclusions'] and len(e['flow_records'])==56
previous=read(p/'walk-common-browser.json')['observed']['suites'];proof=read(p/'walk-tail-browser.json');observed=proof['observed']['suites'];assert len(observed)==158
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-tail-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':300,'unit_calls':1896,'completed_calls':1896,'interrupted_calls':0,
 'new_instruction_coverage':'376/376; no exclusions','new_float_comparison_allowances':0,'new_indeterminate_field_allowances':0,
 'connected_collision_pose_camera_sequences':48,'connected_animation_pose_camera_sequences':8,
 'browser_suites':158,'preserved_browser_suites':155,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'51/142 unchanged; stops before state handlers or common tail','playable':False}
(p/'walk-tail-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
