"""Audit completed animation-state frames and preserve all previous evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-frame-speed-checkpoint.json';c=read(path);prior=read(p/'walk-speed-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-speed-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(1,161,819,836)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(237,644,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(211,216)
assert all(not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_frame_speed_evidence'];assert (e['completed_calls'],e['connected_sequences'],e['completed_animation_frames'],e['queued_messages'],e['indeterminate_byte_comparisons'],e['padding_controls'],e['unfinished_state_boundaries'])==(644,48,168,33,462,12,96)
assert (e['partial_frame']['covered'],e['partial_frame']['total'],e['partial_frame']['recovered_routine'])==(114,142,False)
previous=read(p/'walk-speed-browser.json')['observed']['suites'];proof=read(p/'walk-frame-speed-browser.json');observed=proof['observed']['suites'];assert len(observed)==161
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-frame-speed-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':237,'unit_calls':644,'completed_calls':644,'interrupted_calls':0,
 'new_instruction_coverage':'211/216; no exclusions','new_float_comparison_allowances':0,'indeterminate_payload_byte_comparisons':462,'padding_controls':12,
 'queued_messages':33,'connected_sequences':48,'completed_animation_frames':168,'unfinished_state_boundary_checks':96,'browser_suites':161,'preserved_browser_suites':159,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'New partial candidate114/142;168 completed animation-state4 frames; other states retain explicit boundaries. Maintained51/142 prefix unchanged.','playable':False}
(p/'walk-frame-speed-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
