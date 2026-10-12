"""Audit rail climbing and exits while retaining every previous pinned byte."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-rail-climb-checkpoint.json';c=read(path);prior=read(p/'walk-air-flight-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-air-flight-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(8,179,843,860)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(369,1286,0)
assert sum(x['total'] for x in c['instruction_coverage'].values())==716 and sum(x['covered'] for x in c['instruction_coverage'].values())==716
assert all(not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_rail_climb_evidence'];assert (e['qb_callbacks'],e['indeterminate_probe_word_comparisons'],e['new_numeric_allowances'],e['indeterminate_padding_byte_comparisons'])==(48,177,0,324)
assert (e['connected_exit_sequences'],e['ground_completions'],e['air_completions'],e['original_rail_reentries'],e['common_loop_calls'],e['checker_changes'])==(8,6,2,4,400,0)
assert not e['common_loop_coverage']['recovered_routine'] and e['common_loop_coverage']['covered']==133
previous=read(p/'walk-air-flight-browser.json')['observed']['suites'];proof=read(p/'walk-rail-climb-browser.json');observed=proof['observed']['suites'];assert len(observed)==179
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-rail-climb-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':369,'unit_calls':1286,'completed_calls':1286,'interrupted_calls':0,
 'new_instruction_coverage':'716/716; no exclusions','new_float_comparison_allowances':0,'indeterminate_probe_word_comparisons':177,'indeterminate_padding_byte_comparisons':324,'checker_changes':0,
 'qb_callbacks':48,'connected_exit_sequences':8,'original_rail_reentries':4,'browser_suites':179,'preserved_browser_suites':176,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'Rail frames and exit callbacks validated;133/142 common-loop instructions across400 frames. Hanging remains a boundary and dispatcher uncounted. Maintained51/142 prefix unchanged.','playable':False}
(p/'walk-rail-climb-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
