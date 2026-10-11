"""Pin original SkaterGap startup/frame evidence and the preserved Rotate chain."""
import hashlib,json,struct,zlib
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-gap-checkpoint.json';assert not target.exists()
prior_path=p/'skater-rotate-checkpoint.json'
assert sha(prior_path)=='73c695470bb27f28ebce45a983212882ad1e9255f14a4568f3ddddce91069b83'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-gap-draft.build.json');module=p/'skater-gap-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='ef31b9705c6fe81a796a30ec4e058c07ac4420016ae33ef93fc9f9d19fb02974'
assert module.stat().st_size==813779
previous=read(p/'skater-rotate-browser.json')['observed']['suites']
names=['skater-gap']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-gap-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==136
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-gap-original.json');fixture=read(p/'skater-gap-fixtures.json');result=suites['skater_gap']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(364,708,16,0)
assert unit['cases']==len(fixture['cases'])==364
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==708
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==11
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(343,348)
assert sum(len(row['missing']) for row in coverage.values())==5
assert not any(row['excluded'] for row in coverage.values())
assert all(not row['missing'] for at,row in coverage.items() if at!='0x512c60')
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',233,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==next(c for c,t in row['components'] if t==0xd262802f) and row['score']['state']!=0
 assert row['next_type']==('0x9f9cc949' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
shared=unit['shared_startup_records'];frames=unit['frame_records']
assert len(shared)==2 and [row['reverse_order'] for row in shared]==[False,True]
for row in shared:
 assert set(row['components'])=={'0x11b4c67f','0x43686585','0xd9151d4d','0x5bd63b29'}
 assert len(set(row['components'].values()))==4
assert len(frames)==45 and unit['counts']['thug_skater_gap_update_draft']==141
assert suites['skater_rotate']['double_return_bit_checks']==366 and suites['skater_rotate']['nan_double_returns_checked_exactly']==2
assert suites['skater_matrix']['fcos_infinity_cases']==2 and suites['skater_matrix']['fcos_infinity_emulator_differences']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-gap-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
paths=set(p.glob('*skater-gap*'))|set((p/'skater-gap-next-ghidra').rglob('*'))|{prior_path,p/'skater-rotate-audit.json'}
for key,row in {**read(p/'skater-gap-names.json'),**read(p/'skater-gap-next-names.json')}.items():
 file=r/row['path'];data=file.read_bytes();raw=row['name'].encode('latin1');paths.add(file)
 assert sha(file)==row['sha256']
 assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(key,16))+raw+b'\0'
 assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(key,16)
routines=read(p/'skater-gap-routines.json');assert routines['specimen_sha256']==unit['specimen_sha256']
assert {row['address'] for row in routines['complete_routines']}==set(coverage)
for row in routines['complete_routines']:assert row['instructions']==coverage[row['address']]['total']
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-gap-next.txt',p/'skater-gap-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':11,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+11,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+11,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':136,'new_cases':364,'new_calls_including_existing_dependencies':708,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'skater_gap_shared_startup':shared,'skater_gap_frames':frames,
 'unrecovered_lifecycle':'SkaterGap startup, frame cancellation and secondary cleanup are recovered. Gap start/end scoring and checksum commands still trap. Local skater construction creates Gap and stops before9f9cc949 SkaterAdjustPhysics; nonlocal850eef66 is unchanged. Remaining skater assembly, Trick/PhysicsControl frame/commands, Score frame/commands/disposal, Input binding, camera, rendering and playable training remain unfinished.',
 'coverage_limit':'343/348 new instructions exercised. Five factory allocation-failure instructions are unexercised, with no exclusions. Partial582d90 reaches233/463 in32 interrupted calls and is not counted complete. Eleven complete routines cover Gap construction/factory/init/links/destruction/delete, two sentinel wrappers, state-mask selection, frame cancellation and secondary-list cleanup. Every return, arena/global/heap byte and completed-call preserved register compares; no float or NaN allowances. Successful allocation, valid internal graphs and circular lists are fixture contracts. StartGap, EndGap and command dispatch remain unrecovered. No complete skater, cold boot or playable frame is claimed.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
