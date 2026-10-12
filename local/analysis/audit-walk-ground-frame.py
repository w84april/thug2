"""Audit completed ground-state frames and preserve all previous evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-ground-frame-checkpoint.json';c=read(path);prior=read(p/'walk-frame-speed-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-frame-speed-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(2,164,821,838)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(348,584,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(285,287)
assert all(not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_ground_frame_evidence'];assert (e['completed_calls'],e['connected_sequences'],e['completed_ground_frames'],e['successful_transfers'],e['queued_messages'],e['indeterminate_word_comparisons'],e['indeterminate_byte_comparisons'],e['padding_controls'],e['cache_lifetime_controls'],e['unfinished_state_boundaries'])==(584,56,242,4,32,731,240,12,5,80)
assert (e['partial_frame']['covered'],e['partial_frame']['total'],e['partial_frame']['recovered_routine'])==(131,142,False)
previous=read(p/'walk-frame-speed-browser.json')['observed']['suites'];proof=read(p/'walk-ground-frame-browser.json');observed=proof['observed']['suites'];assert len(observed)==164
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-ground-frame-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':348,'unit_calls':584,'completed_calls':584,'interrupted_calls':0,
 'new_instruction_coverage':'285/287; no exclusions','new_float_comparison_allowances':0,'indeterminate_probe_word_comparisons':731,'indeterminate_payload_byte_comparisons':240,'padding_controls':12,'cache_lifetime_controls':5,'live_cache_observations':8,
 'queued_messages':32,'connected_sequences':56,'completed_ground_frames':242,'integrated_transfer_cases':12,'successful_transfers':4,'event_callbacks':22,'additional_animation_frames':168,'additional_time_advances':168,'unfinished_state_boundary_checks':80,'browser_suites':164,'preserved_browser_suites':161,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'New partial candidate131/142;242 completed ground-entry frames. Separate168 animation frames pass through the same export. Air/hang/rail retain explicit boundaries. Maintained51/142 prefix unchanged.','playable':False}
(p/'walk-ground-frame-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
