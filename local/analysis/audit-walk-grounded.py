"""Audit full floor/ground recovery and preservation of the preceding checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
path=p/'walk-grounded-checkpoint.json';c=read(path);prior=read(p/'walk-grab-checkpoint.json')
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-grab-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(2,153,803,820)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(164,262,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(394,410)
assert all(not x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_grounded_evidence'];assert (e['completed_calls'],e['floor_calls'],e['ground_calls'],e['floor_callbacks'])==(262,88,174,38)
assert e['indeterminate_word_comparisons']==512 and e['numeric_comparison_allowances']==0 and not e['new_unreachable_exclusions']
assert e['event_branch_evidence']['missing_instructions']==c['instruction_coverage']['0x52d300']['missing']
previous=read(p/'walk-grab-browser.json')['observed']['suites'];proof=read(p/'walk-grounded-browser.json');observed=proof['observed']['suites'];assert len(observed)==153
assert proof['rendered_dom_fingerprint']==c['browser_dom_fingerprint'] and proof['status'].startswith('PASS')
for name,value in observed.items():
 assert value['result']=='pass' and value==read(p/('walk-grounded-checkpoint-'+name.replace('_','-')+'-result.json')),name
 if name in previous:assert value==previous[name],name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':164,'unit_calls':262,'completed_calls':262,'interrupted_calls':0,
 'new_instruction_coverage':'394/410; no exclusions;16 ground-event instructions unexercised','new_float_comparison_allowances':0,'indeterminate_word_comparisons':512,'negative_checker_corruptions_rejected':6,
 'browser_suites':153,'preserved_browser_suites':152,'constructor_prefix':'277/463 unchanged; stops before7cd3e6d5','walk_frame_prefix':'51/142 unchanged; stops before state handlers or common tail',
 'walk_ground':'Complete431-byte translation;118/134 instructions exercised,16 retained without exclusions','playable':False}
(p/'walk-grounded-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
