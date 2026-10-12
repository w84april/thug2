"""Audit the component-loop integration and immutable previous evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-component-checkpoint.json';c=read(path);prior=read(p/'walk-hanging-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','coverage_limit','scope','unrecovered_lifecycle','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-hanging-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(0,185,853,870)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(168,797,0)
assert c['original_addresses']==[] and not c['playable']
e=c['walk_component_evidence'];assert (e['object_loop_calls'],e['walking_frames'],e['qb_callbacks'],e['constructed_bound_state_cases'],e['new_routine_count'])==(571,492,27,5,0)
assert (e['indeterminate_probe_word_comparisons'],e['indeterminate_padding_byte_comparisons'],e['numeric_allowances'],e['checker_changes'])==(283,762,0,0)
assert e['prior_module_rejected'] and e['other_component_frames']=='suspended'
previous=read(p/'walk-hanging-browser.json')['observed']['suites'];proof=read(p/'walk-component-browser.json');observed=proof['observed']['suites'];assert len(observed)==185
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-component-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':168,'unit_calls':797,'completed_calls':797,'interrupted_calls':0,'new_routines':0,
 'integration_instruction_coverage':'183/183 across existing object-loop and walking routines; no new routine count','new_float_comparison_allowances':0,'indeterminate_probe_word_comparisons':283,'indeterminate_padding_byte_comparisons':762,'checker_changes':0,
 'object_loop_calls':571,'walking_frames':492,'qb_callbacks':27,'constructed_bound_state_cases':5,'connected_hang_exit_sequences':16,'pre_frame_script_cases':7,'nested_collision_script_cases':8,'prior_module_rejected':True,
 'browser_suites':185,'preserved_browser_suites':184,'constructor_prefix':'277/463 unchanged; stops before SkaterLocalNetLogic 7cd3e6d5','walk_frame':'Complete dispatcher reached through real component update slot. Other component frame methods remain suspended in integration fixtures.','playable':False}
(p/'walk-component-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
