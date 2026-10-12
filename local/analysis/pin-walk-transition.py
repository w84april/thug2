"""Pin verified Walk transitions and vertical-rail entry; preserve earlier evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'walk-ground-checkpoint.json';assert sha(prior_path)=='6e4794a6221f713a722b5087b52f625d7d5b73f3b04f40be71d35855a55606ec'
prior=read(prior_path);target=p/'walk-transition-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-transition-draft.build.json');module=p/'walk-transition-draft.wasm'
assert sha(module)==b['sha256']=='e5cef2b1e1b160044f52ccfc7c037b7b2dacc803432ec10d062ae3567aee66fa'
assert module.stat().st_size==869361 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'walk-ground-browser.json')['observed']['suites']
suites={name:read(p/('walk-transition-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_transition',*previous]}
assert len(suites)==149
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-transition-original.json');fixture=read(p/'walk-transition-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-transition-routines.json')
assert (original['cases'],original['calls'],suites['walk_transition']['cases'],suites['walk_transition']['calls'])==(825,1399,825,1399)
assert original['counts']==suites['walk_transition']['counts'] and suites['walk_transition']['nan_fields_classification_only']==0
assert len(coverage)==11 and set(coverage)==set(routines)
extents=read(p/'walk-transition-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-transition-routines.json')
assert set(extents['checked'])==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(1011,1014)
exclusions=read(p/'walk-transition-exclusions.json')
for at,row in coverage.items():assert set(row['missing'])==set(row['excluded']) and row['excluded']==exclusions.get(at,{})
assert sum(len(x['excluded']) for x in coverage.values())==3 and not fixture['float_fields']
for case in fixture['cases']:
 for step in case['steps']:
  assert not step.get('expected_trap')
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
assert suites['walk_transition']['virtual_wait_callbacks']==0
sequences=original['rail_sequence_records'];assert len(sequences)==12
assert all(row['callback']=='0x4410c0' and row['final_state']==3 for row in sequences)
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-transition-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-transition-*'))|{prior_path,p/'walk-ground-audit.json'}
paths.update(p/name for name in ['audit-walk-transition.py','build-walk-transition-draft.py','pin-walk-transition.py','probe-walk-transition.py','serve-walk-transition.py','verify-walk-transition-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-transition-next.txt',p/'walk-transition-audit.json',p/'walk-transition-preliminary-result.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':11,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':782,'unpromoted_functions_across_separate_experiments':799,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':149,
 'new_cases':825,'new_calls_including_existing_dependencies':1399,'new_interrupted_calls':0,'instruction_coverage':coverage,
 'coverage_limit':'1011/1014 new instructions exercised; three success-path reference cleanup instructions are unreachable after a false query result. All1399 comparison calls complete. Initialized graphs, valid rail links/counts and finite numeric fixtures are contracts. No NaN classification, numeric masks, quieting or uninitialized-byte allowances. Twelve explicit search-to-callback-target sequences do not recover the intervening movement/animation frame. Existing trigonometric and PC24 arithmetic retain the established emulator model; physical processor transcendental accuracy is not newly established.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Walk state-change and vertical-rail selection/entry helpers are recovered, including callback-target initialization. Ground parent52d300 remains18/134 and stops before52c2c0, whose ledge helper52bc70 remains unfinished. Floor/contact handler52b370, full ground/Walk and intervening animation frames, remaining startup, renderer creation/rendering and original playable training remain unfinished. Constructor277/463 and common Walk frame51/142 are unchanged.',
 'walk_transition_evidence':{'completed_calls':1399,'interrupted_calls':0,'rail_sequence_records':sequences,'unexercised_instructions':3,'unreachable_exclusions':exclusions},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
