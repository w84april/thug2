"""Verify pinned level links and score dependency source and evidence, preserving the entire prior checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'gap-links-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'gap-start-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope','partial_command_dispatch'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'gap-start-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(16,141,714,731)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(360,998,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(508,520)
assert c['partial_command_dispatch']['covered']==71 and c['partial_command_dispatch']['total']==126 and not c['partial_command_dispatch']['counted_as_complete']
assert not any(x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
assert c['combined_command_coverage']=={'covered':121,'total':126,'missing':['0x512e09','0x512e0d','0x512e11','0x512e12','0x512e13'],'source_suites':['gap-start','gap-links'],'counted_as_complete':False}
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':360,'unit_calls':998,
 'new_instruction_coverage':'508/520; heap initialization, allocation failure and null-successor exits unexercised; no exclusions',
 'browser_suites':141,'preserved_browser_suites':140,'constructor_prefix_unchanged':'241/463; local path stops before Trigger','playable':False}
(p/'gap-links-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
