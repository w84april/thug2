"""Pin compared skater startup work; retain all earlier evidence unchanged."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-construction-checkpoint.json';assert not target.exists()
prior_path=p/'input-command-checkpoint.json'
assert sha(prior_path)=='c763e7b6bee6428ca21efa7b234cf3107108da24c0617c0f0ba1dde2484093fd'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-construction-draft.build.json');module=p/'skater-construction-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='220fcf247420b1529a276ee06f09ea0043c0bb0e5096acab64f9d194df716155'
assert module.stat().st_size==795179
previous=read(p/'input-command-browser.json')['observed']['suites']
names=['skater-construction']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-construction-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==130
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-construction-original.json');fixture=read(p/'skater-construction-fixtures.json');result=suites['skater_construction']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(114,228,11,0)
assert unit['cases']==len(fixture['cases'])==114
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==228
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==8
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(161,175)
assert sum(len(row['missing']) for row in coverage.values())==14
assert not any(row['excluded'] for row in coverage.values())
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',145,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['native_callbacks'][0]['module']=='skater-construction-diagnostic-fixture.wasm'
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-construction-browser.json');assert proof['observed']==candidate
assert proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
paths=set(p.glob('*skater-construction*'))|set(p.glob('skater-components-*'))|set((p/'skater-components-ghidra').rglob('*'))|set(p.glob('*skater-score*'))|set((p/'skater-score-discovery-ghidra').rglob('*'))|{prior_path,p/'input-command-audit.json'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-construction-next.txt',p/'skater-construction-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':list(coverage),
 'partial_original_addresses':prior['partial_original_addresses']+['0x582d90'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+8,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+8,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':130,'new_cases':114,'new_calls_including_existing_dependencies':228,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'skater_constructor_prefix':prefix,
 'unrecovered_lifecycle':'Original skater registration and initial Suspend, bounds, State, attachment and local Input creation execute. The partial constructor deliberately stops before Score creation at45ee20. Input binding, remaining skater assembly, camera, rendered frames, production audio/file services and a playable original training level remain unfinished. Earlier training traces are preserved unchanged.',
 'coverage_limit':'161/175 instructions in eight complete routines exercised; fourteen allocation-failure instructions remain unexercised, with no exclusions. Separately,145/463 constructor instructions execute in32 interrupted calls. Formatter401c30 is an explicit debug-output argument boundary. Skater/node method tables are identity storage only; attachment disposal and command dispatch explicitly trap. State command registration is pending. No constructor completion or playable scene is claimed. Earlier limits remain in the immutable prior checkpoint.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
