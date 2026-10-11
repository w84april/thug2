"""Pin AdjustPhysics startup and moving-surface escape after both runtimes pass."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-adjust-checkpoint.json';assert not target.exists()
prior_path=p/'skater-gap-checkpoint.json'
assert sha(prior_path)=='171a906648849d705c4cffaf78a39f9737a90f118b7d20d3a700c65e41ce2a06'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-adjust-draft.build.json');module=p/'skater-adjust-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='d6ef5dd16778a05454f611f403283c27bbea3b856cd25365cfe2419e65da7d27'
assert module.stat().st_size==817121
previous=read(p/'skater-gap-browser.json')['observed']['suites']
names=['skater-adjust']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-adjust-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==137
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-adjust-original.json');fixture=read(p/'skater-adjust-fixtures.json');result=suites['skater_adjust']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(313,565,14,0)
assert unit['cases']==len(fixture['cases'])==313
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==565
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==8
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(355,376)
assert not any(row['excluded'] for row in coverage.values())
assert len(coverage['0x4f80e0']['missing'])==7 and len(coverage['0x427700']['missing'])==14
assert all(not row['missing'] for at,row in coverage.items() if at not in ['0x4f80e0','0x427700'])
routines=read(p/'skater-adjust-routines.json');assert set(routines)==set(coverage)
for at,row in routines.items():assert row['instructions']==coverage[at]['total']
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',241,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==next(c for c,t in row['components'] if t==0xd262802f) and row['score']['state']!=0
 assert row['next_type']==('0xe594f0a2' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
shared=unit['shared_startup_records'];assert [row['reverse_order'] for row in shared]==[False,True]
for row in shared:assert set(row['components'])=={'0x9f9cc949','0x43686585','0x5bd63b29'} and len(set(row['components'].values()))==3
evidence=read(p/'skater-adjust-evidence.json')
assert evidence['escape_first_call_outcomes']=={'restore previous':48,'surface plus one':13,'velocity candidate':11}
assert suites['skater_rotate']['double_return_bit_checks']==366 and suites['skater_rotate']['nan_double_returns_checked_exactly']==2
assert suites['skater_matrix']['fcos_infinity_cases']==2 and suites['skater_matrix']['fcos_infinity_emulator_differences']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-adjust-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
paths=set(p.glob('*skater-adjust*'))|set((p/'skater-adjust-ghidra').rglob('*'))|{prior_path,p/'skater-gap-audit.json'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-adjust-next.txt',p/'skater-adjust-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+8,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+8,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':137,'new_cases':313,'new_calls_including_existing_dependencies':565,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'skater_adjust_shared_startup':shared,'moving_escape_evidence':evidence,
 'unrecovered_lifecycle':'AdjustPhysics startup and moving containment/escape prerequisites recovered. Complete frame4f8c40, escape integration4f8aa0, ground correction4f8420 and surface/model lighting4f82f0/420670 remain unrecovered; the update slot traps. Local construction creates Adjust and stops before Trigger e594f0a2; remote850eef66 unchanged. Gap scoring/commands, remaining skater assembly, Trick/PhysicsControl frame/commands, Score frame/commands/disposal, Input binding, camera, rendering and playable training remain unfinished.',
 'coverage_limit':'355/376 new instructions exercised, with seven allocation-failure and fourteen probe-cleanup instructions unexercised; no exclusions. All115 escape instructions exercised. Partial582d90 reaches241/463 in32 interrupted calls and is not counted complete. Every return, arena/global/heap byte and completed-call preserved register compares without float or NaN allowances. Valid initialized graphs, successful allocation, finite collision geometry and bounded scene storage are fixture contracts. New moving collision fixtures are synthetic geometry, not an actual training skater. Full frame/ground/light integration, cold boot and playability remain unfinished.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
