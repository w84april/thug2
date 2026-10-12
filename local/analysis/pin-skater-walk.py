"""Pin verified Walk startup/common frame recovery and preserve older evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
prior_path=p/'skater-cleanup-checkpoint.json';assert sha(prior_path)=='e0ddda94d392f6197f33dad0747c1705460c4d609f22bf041eca4b5e2348cbd1'
prior=read(prior_path);target=p/'skater-walk-checkpoint.json';assert not target.exists()
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
b=read(p/'skater-walk-draft.build.json');module=p/'skater-walk-draft.wasm'
assert sha(module)==b['sha256']=='0ae07a7452cbffe29a672a7cf71a2c4c4ead9a12131c2aadb7e84960ae80d6b3'
assert module.stat().st_size==857498 and b['source_hashes']==prior['source_hashes']
for name,digest in {**b['source_hashes'],**b['draft_source_hashes'],**b['derived_from']}.items():assert sha(r/name)==digest,name
adapter=read(p/'skater-walk-memory.build.json')
assert adapter['sha256']==sha(p/'skater-walk-memory.wasm')
for name,digest in adapter['source_hashes'].items():assert sha(r/name)==digest,name
previous=read(p/'skater-cleanup-browser.json')['observed']['suites']
suites={name:read(p/('skater-walk-checkpoint-'+name.replace('_','-')+'-result.json')) for name in ['skater_walk',*previous]}
assert len(suites)==147
for name,result in suites.items():
 assert result['result']=='pass',name
 if name in previous:assert result==previous[name],name
original=read(p/'skater-walk-original.json');fixture=read(p/'skater-walk-fixtures.json');coverage=original['instruction_coverage'];routines=read(p/'skater-walk-routines.json')
assert (original['cases'],original['calls'],suites['skater_walk']['cases'],suites['skater_walk']['calls'])==(848,1474,848,1474)
assert original['counts']==suites['skater_walk']['counts'] and suites['skater_walk']['nan_fields_classification_only']==0
assert len(coverage)==11 and set(coverage)==set(routines)
extents=read(p/'skater-walk-extents.json');assert extents['result']=='pass' and extents['routines_sha256']==sha(p/'skater-walk-routines.json')
assert set(extents['checked'])==set(routines)
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(505,505)
assert not any(x['missing'] or x['excluded'] for x in coverage.values()) and not fixture['float_fields']
interrupted={'0x582d90':0,'0x52d4b0':0};frame_targets=set()
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_quiet_float_indices','global_bit_masks','float_fields','global_float_indices','indeterminate_bytes','compression_records'])
  if step.get('expected_trap'):
   assert step['fn'] in interrupted;interrupted[step['fn']]+=1
   if step['fn']=='0x52d4b0':frame_targets.add(step['boundary_factory'])
assert interrupted=={'0x582d90':32,'0x52d4b0':112}
assert frame_targets=={0x52d300,0x52cef0,0x440bf0,0x4425b0,0x52ad10,0x52d563}
assert suites['skater_walk']['virtual_wait_callbacks']==0
failure=fixture['cases'][fixture['case_labels'].index('factory allocation failure')]
assert len(failure['steps'])==2 and all(s['fn']=='0x52a5c0' and s['result']==0 for s in failure['steps'])
constructor=original['partial_constructor'];frame=original['partial_frame']
assert (constructor['covered'],constructor['total'],constructor['interrupted_calls'])==(277,463,32)
assert (frame['covered'],frame['total'],frame['interrupted_calls'])==(51,142,112)
assert prior['skater_constructor_prefix']['covered']==265
for record in constructor['records']:
 local=record['arguments'][2]&255;types=[kind for _,kind in record['components']]
 assert record['next_type']==('0x7cd3e6d5' if local else '0x850eef66')
 assert (0x726e85aa in types)==bool(local)
 assert record['boundary'][0]==0x45ee20 and record['boundary'][3]==1
for name in prior['artifact_hashes']:
 if name.endswith('-routines.json'):
  old=read(r/name)
  if isinstance(old,dict):assert not set(routines).intersection(old),name
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-walk-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
assert proof['rendered_dom_fingerprint']==fingerprint(candidate)
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
paths=set(p.glob('skater-walk-*'))|{prior_path,p/'skater-cleanup-audit.json'}
paths.update(p/name for name in ['audit-skater-walk.py','build-skater-walk-draft.py','pin-skater-walk.py','probe-skater-walk.py','serve-skater-walk.py','verify-skater-walk-checkpoint.mjs'])
for f in paths:
 if f.is_file() and f.suffix!='.log' and f not in [target,p/'skater-walk-next.txt',p/'skater-walk-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':11,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':764,'unpromoted_functions_across_separate_experiments':781,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'browser_suites':147,
 'new_cases':848,'new_calls_including_existing_dependencies':1474,'new_interrupted_calls':144,'instruction_coverage':coverage,
 'coverage_limit':'505/505 new instructions exercised, not exhaustive inputs or branches. Of1474 calls,1330 complete and144 explicitly stop (32 constructor and112 frame-prefix). Factory allocation failure is exercised at the test-heap boundary. Initialized dependency graphs and required QB parameters are contracts. No NaN classification, numeric masks, quieting allowances or uninitialized-byte allowances in this suite. Existing platform sine/cosine and PC24 arithmetic retain the previously established emulator model; physical processor transcendental accuracy is not newly established.',
 'scope':fixture['scope'],
 'unrecovered_lifecycle':'Walk lifecycle/input/owner vectors/score decay are recovered. Local skater construction now stops before7cd3e6d5; remote850eef66 unchanged. Walk common frame setup stops before its five state handlers or remaining common tail. State movement/collision behavior, remaining startup/frames, renderer creation/rendering and original playable training remain unfinished.',
 'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':constructor,
 'walk_evidence':{'completed_calls':1330,'interrupted_calls':144,'partial_frame':frame,'shared_startup_records':original['shared_startup_records'],'allocation_failure_calls':2,'checker_per_step_boundaries':True},
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False}
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
