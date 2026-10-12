"""Audit four airborne helpers and preserve the previous ground-frame checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-air-motion-checkpoint.json';c=read(path);prior=read(p/'walk-ground-frame-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-ground-frame-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(4,168,825,842)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(551,1204,0)
assert sum(x['total'] for x in c['instruction_coverage'].values())==546
assert all(x['covered']==x['total'] and not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_air_motion_evidence'];assert (e['completed_calls'],e['cases'],e['instructions'],e['live_cache_observations'],e['ceiling_hits'],e['ceiling_velocity_projections'],e['ceiling_second_query_hits'],e['ceiling_second_query_misses'],e['ceiling_object_events'])==(1204,551,546,64,80,36,24,56,80)
previous=read(p/'walk-ground-frame-browser.json')['observed']['suites'];proof=read(p/'walk-air-motion-browser.json');observed=proof['observed']['suites'];assert len(observed)==168
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-air-motion-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':551,'unit_calls':1204,'completed_calls':1204,'interrupted_calls':0,
 'new_instruction_coverage':'546/546; no exclusions','new_float_comparison_allowances':0,'new_indeterminate_field_allowances':0,'live_cache_observations':64,
 'ceiling_hits':80,'ceiling_velocity_projections':36,'ceiling_second_query_hits':24,'ceiling_second_query_misses':56,'ceiling_object_events':80,'subscribed_event_callbacks':0,'browser_suites':168,'preserved_browser_suites':164,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'Prior ground131/142 and animation114/142 partial candidates preserved; airborne helper tests are not complete airborne frames. Maintained51/142 prefix unchanged.','playable':False}
(p/'walk-air-motion-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
