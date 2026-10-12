"""Pin verified Walk ground helpers and preserve all earlier evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'skater-walk-checkpoint.json';assert sha(prior_path)=='ad6425b0bc8f7f24c600967702cfbde8619d573d550179581af1efed4c9f94c9'
prior=read(prior_path);target=p/'walk-ground-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'walk-ground-draft.build.json');module=p/'walk-ground-draft.wasm'
assert sha(module)==b['sha256']=='5867b6b3651e096f6a4e8f611fde0c9d6c78380591e173ce8710f258575f9e1a'
assert module.stat().st_size==863701 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'skater-walk-browser.json')['observed']['suites']
suites={name:read(p/('walk-ground-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['walk_ground',*previous]}
assert len(suites)==148
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'walk-ground-original.json');fixture=read(p/'walk-ground-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'walk-ground-routines.json')
assert (original['cases'],original['calls'],suites['walk_ground']['cases'],suites['walk_ground']['calls'])==(485,953,485,953)
assert original['counts']==suites['walk_ground']['counts'] and suites['walk_ground']['nan_fields_classification_only']==0
assert len(coverage)==7 and set(coverage)==set(routines)
extents=read(p/'walk-ground-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'walk-ground-routines.json')
assert set(extents['checked'])==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(1249,1259)
exclusions=read(p/'walk-ground-exclusions.json')
for at,row in coverage.items():assert set(row['missing'])==set(row['excluded']) and row['excluded']==exclusions.get(at,{})
assert sum(len(x['excluded']) for x in coverage.values())==10 and not fixture['float_fields']
interrupted=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  if step.get('expected_trap'):
   assert step['fn']=='0x52d300' and step['boundary_factory']==0x52c2c0;interrupted+=1
assert interrupted==12 and suites['walk_ground']['virtual_wait_callbacks']==0
prefix=original['partial_ground'];assert (prefix['covered'],prefix['total'],prefix['interrupted_calls'])==(18,134,12)
assert all(record['boundary']=='0x52c2c0' for record in prefix['records'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'walk-ground-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('walk-ground-*'))|{prior_path,p/'skater-walk-audit.json'}
paths.update(p/name for name in ['audit-walk-ground.py','build-walk-ground-draft.py','pin-walk-ground.py','probe-walk-ground.py','serve-walk-ground.py','verify-walk-ground-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'walk-ground-next.txt',p/'walk-ground-audit.json',p/'walk-ground-preliminary-result.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':771,'unpromoted_functions_across_separate_experiments':788,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':148,
 'new_cases':485,'new_calls_including_existing_dependencies':953,'new_interrupted_calls':12,'instruction_coverage':coverage,
 'coverage_limit':'1249/1259 new instructions exercised; ten documented unreachable paths under the stable initialized single-threaded graph, not exhaustive inputs or branches. Of953 calls,941 complete and12 explicitly stop before ground transition52c2c0. No NaN classification, numeric masks, quieting or uninitialized-byte allowances in this suite. Required QB parameters and finite numeric inputs are fixture contracts. Existing platform sine/cosine and PC24 arithmetic retain the established emulator model; physical processor transcendental accuracy is not newly established.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Walk ground platform/cache/facing/speed/steering/step-height helpers are recovered. Ground parent52d300 stops before52c2c0; floor/contact handler52b370 remains unfinished. Constructor277/463 and common Walk frame51/142 remain unchanged. Remaining ground transitions, other movement states, startup, renderer creation/rendering and original playable training remain unfinished.',
 'walk_ground_evidence':{'completed_calls':941,'interrupted_calls':12,'partial_ground':prefix,'unexercised_instructions':10,'unreachable_exclusions':exclusions},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
