"""Pin the completed AdjustPhysics frame after exact original/Node/Chromium checks."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-ground-checkpoint.json';assert not target.exists()
prior_path=p/'skater-adjust-checkpoint.json';assert sha(prior_path)=='919da83f00e7b4d13ea48c0b75fca6284a9802edad0304a973794f18461cd6e5';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-ground-draft.build.json');module=p/'skater-ground-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='918f1c47860a908dacd76205b3875880348aa04274080920feb91070543db834'
assert module.stat().st_size==823912
previous=read(p/'skater-adjust-browser.json')['observed']['suites'];names=['skater-ground']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-ground-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==138
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-ground-original.json');fixture=read(p/'skater-ground-fixtures.json');result=suites['skater_ground']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(478,1032,16,0)
assert unit['cases']==len(fixture['cases'])==478 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1032
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==14
assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(955,960)
assert not any(x['excluded'] for x in coverage.values())
assert {a:x['missing'] for a,x in coverage.items() if x['missing']}=={'0x48e660':['0x48e6b7','0x48e6be'],'0x4f82f0':['0x4f83ee','0x4f83f5','0x4f83f6']}
routines=read(p/'skater-ground-routines.json');assert set(routines)==set(coverage)
for a,x in routines.items():assert x['instructions']==coverage[a]['total']
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
for case in fixture['cases']:
 for step in case['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
evidence=read(p/'skater-ground-evidence.json');assert len(evidence['owner_virtual_frames'])==8 and all(len(row['frames'])==3 for row in evidence['owner_virtual_frames'])
assert (evidence['original_collision_queries'],evidence['original_event_emissions'])==(842,65)
assert suites['skater_rotate']['double_return_bit_checks']==366 and suites['skater_rotate']['nan_double_returns_checked_exactly']==2
assert suites['skater_matrix']['fcos_infinity_cases']==2 and suites['skater_matrix']['fcos_infinity_emulator_differences']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-ground-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
paths=set(p.glob('*skater-ground*'))|{prior_path,p/'skater-adjust-audit.json'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-ground-next.txt',p/'skater-ground-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':14,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+14,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+14,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':138,'new_cases':478,'new_calls_including_existing_dependencies':1032,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'skater_ground_evidence':evidence,
 'unrecovered_lifecycle':'Full SkaterAdjustPhysics frame, moving escape integration, ground correction and surface/model/global lighting are recovered. The actual owner dispatcher reaches the real Adjust update slot. Local skater construction remains at Trigger e594f0a2; remote850eef66 unchanged. Gap scoring/commands, remaining skater assembly, Trick/PhysicsControl frame/commands, Score frame/commands/disposal, Input binding, camera, rendering and playable training remain unfinished.',
 'coverage_limit':'955/960 new instructions exercised: two skipped alignment and three secondary-probe reference-cleanup instructions unexercised, with no exclusions. All423 ground-correction,107 moving-escape and43 frame instructions exercised. All returns, arena/global/heap bytes and preserved registers compare without float/NaN allowances. Synthetic initialized graphs with bounded storage, nondegenerate light hits and finite geometry are fixture contracts. Color arithmetic includes exact quiet-NaN payloads and factor-array overlap. Twenty-four original owner-dispatch frames,842 collision calls and65 event emissions are observed. These fixtures are not playable training-level frames. Full skater, cold boot and rendering remain unfinished.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
