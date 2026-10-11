"""Pin gap creation recovery only after original, Node and rendered Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'gap-score-checkpoint.json';assert sha(prior_path)=='4548a47ac26e99ec593f98963fb83baf72ce0d5ca9acfa33964a1ae96c4133d0'
prior=read(prior_path);target=p/'gap-start-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'gap-start-draft.build.json');module=p/'gap-start-draft.wasm'
assert sha(module)==b['sha256']=='b9a15511ad1b6ff9b5bf331fd14427f2bc0e23dad3604016b934a8f111affce7'
assert module.stat().st_size==831654 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'gap-score-browser.json')['observed']['suites']
suites={name:read(p/('gap-start-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['gap_start',*previous]}
assert len(suites)==140
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
unit=read(p/'gap-start-original.json');fixture=read(p/'gap-start-fixtures.json');routines=read(p/'gap-start-routines.json')
assert (unit['cases'],unit['calls'],suites['gap_start']['cases'],suites['gap_start']['calls'])==(396,984,396,984)
assert unit['counts']==suites['gap_start']['counts'] and suites['gap_start']['nan_fields_classification_only']==0
coverage=unit['instruction_coverage'];assert set(coverage)==set(routines) and len(coverage)==15
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(810,813)
assert {a:x['missing'] for a,x in coverage.items() if x['missing']}=={'0x401dd0':['0x401e13'],'0x578740':['0x5787a3'],'0x512050':['0x512090']}
assert unit['partial_command_dispatch']['covered']==65 and unit['partial_command_dispatch']['total']==126 and not unit['partial_command_dispatch']['counted_as_complete']
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'gap-start-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('*gap-start*'))|{prior_path,p/'gap-score-audit.json'}
for parent in list(paths):
 if parent.is_dir():paths.update(f for f in parent.rglob('*') if f.is_file())
for f in paths:
 if f.is_file() and f not in [target,p/'gap-start-next.txt',p/'gap-start-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':15,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':698,'unpromoted_functions_across_separate_experiments':715,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':140,
 'new_cases':396,'new_calls_including_existing_dependencies':984,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'partial_command_dispatch':unit['partial_command_dispatch'],'coverage_limit':'810/813 instructions exercised; two heap-initialization calls and one allocation-failure branch unexercised, no exclusions or numeric allowances. Allocation success and initialized graphs are required. Signaling-NaN negation matches the Unicorn instruction oracle; physical-x87 signaling behavior is not established.',
 'scope':fixture['scope'].replace('prefix-trigger','linked-node trigger'),'scope_label_correction':'Raw 45c3a0/45c460 read Links 2e7d5ee7; the historical fixture label prefix-trigger refers to linked-node dispatch at checksum4562e4a6.','unrecovered_lifecycle':'Full StartGap, secondary registration/checking, concrete nodes and strings, and gap list cleanup are recovered. Four command routes are wired into the component. EndGap and linked-node trigger dispatch still trap; the dispatcher is partial and not counted complete. Skater construction remains at Trigger; other skater behavior, camera, rendering and playable training are unfinished.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
