"""Audit connected airborne movement while retaining every previous pinned byte."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-air-flight-checkpoint.json';c=read(path);prior=read(p/'walk-air-catch-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-air-catch-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(1,176,835,852)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(266,1000,0)
assert sum(x['total'] for x in c['instruction_coverage'].values())==296 and sum(x['covered'] for x in c['instruction_coverage'].values())==296
assert all(not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_air_flight_evidence'];assert (e['qb_callbacks'],e['indeterminate_probe_word_comparisons'],e['new_numeric_allowances'],e['indeterminate_padding_byte_comparisons'])==(40,1324,0,378)
assert (e['connected_projectile_callbacks'],e['connected_transfer_cases'],e['common_loop_calls'],e['checker_changes'])==(20,4,768,0)
assert not e['common_loop_coverage']['recovered_routine'] and e['common_loop_coverage']['covered']==129
previous=read(p/'walk-air-catch-browser.json')['observed']['suites'];proof=read(p/'walk-air-flight-browser.json');observed=proof['observed']['suites'];assert len(observed)==176
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-air-flight-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':266,'unit_calls':1000,'completed_calls':1000,'interrupted_calls':0,
 'new_instruction_coverage':'296/296; no exclusions','new_float_comparison_allowances':0,'indeterminate_probe_word_comparisons':1324,'indeterminate_padding_byte_comparisons':378,'checker_changes':0,
 'qb_callbacks':40,'connected_projectile_callbacks':20,'connected_transfer_cases':4,'browser_suites':176,'preserved_browser_suites':174,
 'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'Complete air52cef0 validated;129/142 common-loop instructions across768 calls. Hanging/rail frames remain boundaries and dispatcher uncounted. Maintained51/142 prefix unchanged.','playable':False}
(p/'walk-air-flight-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
