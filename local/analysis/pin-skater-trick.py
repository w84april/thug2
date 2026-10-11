"""Pin Trick and PhysicsControl startup recovery and preserve all earlier proof without mutation."""
import hashlib,json,struct,zlib
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-trick-checkpoint.json';assert not target.exists()
prior_path=p/'skater-matrix-checkpoint.json'
assert sha(prior_path)=='503f4318b9bdd07e04cf64e752de6681f4a087419f813ebe35256b5d43fc7278'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-trick-draft.build.json');module=p/'skater-trick-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='2d6247aee0331ca6d6a9e164d614454b3f9fe765bb0e1a0e46c5415b8daf5302'
assert module.stat().st_size==805062
previous=read(p/'skater-matrix-browser.json')['observed']['suites']
names=['skater-trick']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-trick-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==134
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-trick-original.json');fixture=read(p/'skater-trick-fixtures.json');result=suites['skater_trick']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(167,326,18,0)
assert unit['cases']==len(fixture['cases'])==167
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==326
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==12
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(258,269)
assert sum(len(row['missing']) for row in coverage.values())==11
assert not any(row['excluded'] for row in coverage.values())
assert all(not row['missing'] for at,row in coverage.items() if at not in ['0x523490','0x517830'])
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',213,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==next(c for c,t in row['components'] if t==0xd262802f) and row['score']['state']!=0
 assert row['next_type']==('0x52d61a0d' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
shared=unit['shared_startup_records']
assert len(shared)==2 and [row['reverse_order'] for row in shared]==[False,True]
for row in shared:
 assert set(row['components'])=={'0x43686585','0xbf518e27','0x270f56e1','0xd9151d4d','0x5bd63b29'}
 assert len(set(row['components'].values()))==5
assert suites['skater_matrix']['fcos_infinity_cases']==2
assert suites['skater_matrix']['fcos_infinity_emulator_differences']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-trick-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
discovery=read(p/'skater-trick-next-discovery.json');row=discovery['name_record'];name_source=r/row['path']
raw=discovery['name'].encode('latin1');data=name_source.read_bytes()
assert sha(name_source)==row['sha256']
assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(discovery['type'],16))+raw+b'\0'
assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(discovery['type'],16)
paths=set(p.glob('*skater-trick*'))|set((p/'skater-trick-next-ghidra').rglob('*'))|set((p/'skater-trick-control-ghidra').rglob('*'))|{prior_path,p/'skater-matrix-audit.json',name_source}
for key,row in read(p/'skater-trick-next-names.json').items():
 file=r/row['path'];data=file.read_bytes();raw=row['name'].encode('latin1');paths.add(file)
 assert sha(file)==row['sha256']
 assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(key,16))+raw+b'\0'
 assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(key,16)
routines=read(p/'skater-trick-routines.json')
assert routines['specimen_sha256']==unit['specimen_sha256']
assert {row['address'] for row in routines['complete_routines']}==set(coverage)
for row in routines['complete_routines']:assert row['instructions']==coverage[row['address']]['total']
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-trick-next.txt',p/'skater-trick-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':12,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+12,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+12,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':134,'new_cases':167,'new_calls_including_existing_dependencies':326,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'trick_control_shared_startup':shared,
 'unrecovered_lifecycle':'Local original skater construction now creates Trick, PhysicsControl and Physics and stops before SkaterRotate52d61a0d. Nonlocal850eef66 is unchanged. Trick and PhysicsControl frame/commands, Score frame/commands/disposal, Input binding, remaining skater assembly, camera, rendering and playable training remain unfinished. Prior training and Score asset traces are unchanged.',
 'coverage_limit':'258/269 new instructions exercised. Eleven factory allocation-failure instructions are unexercised, with no exclusions. Partial582d90 separately reaches213/463instructions in32 interrupted calls; it is not counted complete. The twelve added routines cover startup and lifetime only. Constructed valid internal graphs and a successful allocator are the fixture contracts. Required State on PhysicsControl finalization is preserved. All returns, arena bytes, globals and heap effects compare exactly for the new suite, without NaN masks. Prior MatrixQueries SDK infinity boundary and all earlier limits remain preserved. No complete skater, cold boot or playable-frame claim.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
