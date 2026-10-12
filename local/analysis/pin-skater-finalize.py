"""Pin FinalizePhysics only after original instructions, Node and actual Chromium agree."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'trigger-checkpoint.json';assert sha(prior_path)=='9ddda74c467b84fd929079c957f3755dd1c5af616e4a7d461c9a52618f0c90db'
prior=read(prior_path);target=p/'skater-finalize-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'skater-finalize-draft.build.json');module=p/'skater-finalize-draft.wasm'
assert sha(module)==b['sha256']=='8616ee21b0bf0d9865acd1609f0151d07a92486957415c20ebd7a2d7519dda3e'
assert module.stat().st_size==846039 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
previous=read(p/'trigger-browser.json')['observed']['suites']
suites={name:read(p/('skater-finalize-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['skater_finalize',*previous]}
assert len(suites)==145
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'skater-finalize-original.json');fixture=read(p/'skater-finalize-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'skater-finalize-routines.json')
assert (original['cases'],original['calls'],suites['skater_finalize']['cases'],suites['skater_finalize']['calls'])==(354,664,354,664)
assert original['counts']==suites['skater_finalize']['counts'] and suites['skater_finalize']['nan_fields_classification_only']==0
assert len(coverage)==7 and set(coverage)==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(375,381)
assert {k:v['missing'] for k,v in coverage.items() if v['missing']}=={'0x511280':['0x5112e7','0x5112eb','0x5112ed','0x5112ee','0x5112f5','0x5112f8']}
assert not any(x['excluded'] for x in coverage.values()) and not fixture['float_fields']
interrupted=0
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  if step.get('expected_trap'):
   assert step['fn']=='0x582d90';interrupted+=1
assert interrupted==32 and suites['skater_finalize']['virtual_wait_callbacks']==0
constructor=original['partial_constructor']
assert (constructor['covered'],constructor['total'],constructor['interrupted_calls'])==(257,463,32)
assert prior['skater_constructor_prefix']['covered']==249
for record in constructor['records']:
 local=record['arguments'][2]&255;types=[kind for _,kind in record['components']]
 assert record['next_type']==('0xd8cc3428' if local else '0x850eef66')
 assert (0x9b373e58 in types)==bool(local)
 assert record['boundary'][0]==0x45ee20 and record['boundary'][3]==1
assert len(original['frame_records'])==105
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-finalize-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('skater-finalize-*'))|{prior_path,p/'trigger-audit.json'}
paths.update(p/name for name in ['audit-skater-finalize.py','build-skater-finalize-draft.py','pin-skater-finalize.py','probe-skater-finalize.py','serve-skater-finalize.py','verify-skater-finalize-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-finalize-next.txt',p/'skater-finalize-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':733,'unpromoted_functions_across_separate_experiments':750,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':145,
 'new_cases':354,'new_calls_including_existing_dependencies':664,'new_interrupted_calls':32,
 'instruction_coverage':coverage,
 'coverage_limit':'375/381 new instructions exercised; six allocation-failure instructions remain in the denominator, with no exclusions. No new numeric masks or uninitialized-byte allowances. Of664 calls,632 complete and32 stop at the explicit next constructor boundary. Initialized dependencies and successful allocations are original caller contracts. The experimental shared vector normalizer now preserves the negative x87 indefinite for infinity times zero; no additional routine is counted.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'FinalizePhysics is recovered and local skater construction now stops before SkaterCleanupState (d8cc3428); the remote850eef66 boundary is unchanged. Remaining startup/frames, actual later score linkage, camera/rendering and original playable training remain unfinished.',
 'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':constructor,
 'finalize_evidence':{'completed_calls':632,'interrupted_calls':32,'frame_records':original['frame_records'],'shared_startup_records':original['shared_startup_records'],'derived_vector_source':'local/analysis/skater-finalize-vector-derived.c'},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
