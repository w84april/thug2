"""Pin Trigger only after original instructions, Node and actual Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'gap-end-checkpoint.json';assert sha(prior_path)=='ac6ad02c90082b6a61eac242db086ff03de593daed16254007c48bc0bcef01a3'
prior=read(prior_path);target=p/'trigger-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'trigger-draft.build.json');module=p/'trigger-draft.wasm'
assert sha(module)==b['sha256']=='d018ea5aa6ad9473183a8ecbb6cad46d8786062f8cfd5188327d578b14958875'
assert module.stat().st_size==842452 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'gap-end-browser.json')['observed']['suites']
suites={name:read(p/('trigger-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['trigger',*previous]}
assert len(suites)==144
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'trigger-original.json');fixture=read(p/'trigger-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'trigger-routines.json')
assert (original['cases'],original['calls'],suites['trigger']['cases'],suites['trigger']['calls'])==(307,513,307,513)
assert original['counts']==suites['trigger']['counts'] and suites['trigger']['nan_fields_classification_only']==0
assert len(coverage)==8 and set(coverage)==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(293,294)
assert {k:v['missing'] for k,v in coverage.items() if v['missing']}=={'0x434ce0':['0x434d0d']}
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
interrupted=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  if step.get('expected_trap'):
   assert step['fn']=='0x582d90';interrupted+=1
assert interrupted==32 and suites['trigger']['virtual_wait_callbacks']==35
constructor=original['partial_constructor']
assert (constructor['covered'],constructor['total'],constructor['interrupted_calls'])==(249,463,32)
assert prior['skater_constructor_prefix']['covered']==241
for record in constructor['records']:
 local=record['arguments'][2]&255;types=[kind for _,kind in record['components']]
 assert record['next_type']==('0x9b373e58' if local else '0x850eef66')
 assert (0xe594f0a2 in types)==bool(local)
 assert record['boundary'][0]==0x45ee20 and record['boundary'][3]==1
assert len(original['frame_records'])==16 and all(x['callbacks']>0 for x in original['frame_records'])
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'trigger-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('trigger-*'))|{prior_path,p/'gap-end-audit.json'}
paths.update(p/name for name in ['audit-trigger.py','build-trigger-draft.py','map-trigger-component-names.py','pin-trigger.py','probe-trigger.py','serve-trigger.py','verify-trigger-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f not in [target,p/'trigger-next.txt',p/'trigger-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':726,'unpromoted_functions_across_separate_experiments':743,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':144,
 'new_cases':307,'new_calls_including_existing_dependencies':513,'new_interrupted_calls':32,
 'instruction_coverage':coverage,
 'coverage_limit':'293/294 new instructions exercised; one skipped alignment instruction remains in the denominator, with no exclusions. No new numeric masks or uninitialized-byte allowances. Of513 calls,481 complete and32 stop at the explicit next constructor boundary. Initialized graphs, required command arrays and successful allocations are original caller contracts.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Trigger is recovered and local skater construction now stops before SkaterFinalizePhysics (9b373e58); the remote850eef66 boundary is unchanged. Remaining startup/frames, actual later score linkage, camera/rendering and original playable training remain unfinished.',
 'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':constructor,
 'trigger_evidence':{'completed_calls':481,'interrupted_calls':32,'native_qb_callbacks':35,'frame_records':original['frame_records'],'shared_startup_records':original['shared_startup_records']},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
