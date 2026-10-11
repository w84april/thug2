"""Pin complete SkaterRotate recovery and preserve all earlier proof without mutation."""
import hashlib,json,struct,zlib
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-rotate-checkpoint.json';assert not target.exists()
prior_path=p/'skater-trick-checkpoint.json'
assert sha(prior_path)=='1a54f14bec50624de579c9e958151ad4a0a03758d0302c0eda8e172d5ce0b8d4'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-rotate-draft.build.json');module=p/'skater-rotate-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='b42b21bbae2b2ea8fb03425c3833e4b7da076cbf7e42544d64cfa1378e3d2c5e'
assert module.stat().st_size==810257
previous=read(p/'skater-trick-browser.json')['observed']['suites']
names=['skater-rotate']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-rotate-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==135
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-rotate-original.json');fixture=read(p/'skater-rotate-fixtures.json');result=suites['skater_rotate']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(809,1646,17,0)
assert unit['cases']==len(fixture['cases'])==809
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1646
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==11
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(679,685)
assert sum(len(row['missing']) for row in coverage.values())==6
assert not any(row['excluded'] for row in coverage.values())
assert all(not row['missing'] for at,row in coverage.items() if at!='0x517d40')
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',221,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==next(c for c,t in row['components'] if t==0xd262802f) and row['score']['state']!=0
 assert row['next_type']==('0x11b4c67f' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','quiet_double_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
shared=unit['shared_startup_records']
assert len(shared)==2 and [row['reverse_order'] for row in shared]==[False,True]
for row in shared:
 assert set(row['components'])=={'0x52d61a0d','0x5bd63b29'}
 assert len(set(row['components'].values()))==2 and row['frame_calls']==4
assert result['double_return_bit_checks']==366 and result['nan_double_returns_checked_exactly']==2
assert suites['skater_matrix']['fcos_infinity_cases']==2
assert suites['skater_matrix']['fcos_infinity_emulator_differences']==1
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-rotate-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
discovery=read(p/'skater-rotate-next-discovery.json');row=discovery['name_record'];name_source=r/row['path']
raw=discovery['name'].encode('latin1');data=name_source.read_bytes()
assert sha(name_source)==row['sha256']
assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(discovery['type'],16))+raw+b'\0'
assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(discovery['type'],16)
paths=set(p.glob('*skater-rotate*'))|set((p/'skater-rotate-next-ghidra').rglob('*'))|{prior_path,p/'skater-trick-audit.json',name_source}
for key,row in read(p/'skater-rotate-names.json').items():
 file=r/row['path'];data=file.read_bytes();raw=row['name'].encode('latin1');paths.add(file)
 assert sha(file)==row['sha256']
 assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(key,16))+raw+b'\0'
 assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(key,16)
routines=read(p/'skater-rotate-routines.json')
assert routines['specimen_sha256']==unit['specimen_sha256']
assert {row['address'] for row in routines['complete_routines']}==set(coverage)
for row in routines['complete_routines']:assert row['instructions']==coverage[row['address']]['total']
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-rotate-next.txt',p/'skater-rotate-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':11,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+11,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+11,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':135,'new_cases':809,'new_calls_including_existing_dependencies':1646,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'skater_rotate_shared_startup':shared,'rotate_double_returns':{'bit_checks':366,'nan_payloads':2},
 'unrecovered_lifecycle':'SkaterRotate lifecycle, frame and rotate command are recovered. Local original skater construction creates Rotate and stops before SkaterGap11b4c67f; nonlocal850eef66 is unchanged. Remaining skater assembly, Trick/PhysicsControl frame/commands, Score frame/commands/disposal, Input binding, camera, rendering and playable training remain unfinished. Earlier original asset and scene traces are unchanged.',
 'coverage_limit':'679/685 new instructions exercised. All rotation/math instructions are covered; six factory allocation-failure instructions are unexercised, with no exclusions. Partial582d90 reaches221/463 in32 interrupted calls and is not counted complete. The eleven complete routines include the full Rotate lifecycle, frame, command and four helpers. Whole memory/globals/heap compare exactly;366 double returns, including2 NaN payloads, compare as raw Wasm i64 bits without JavaScript numeric conversion or NaN allowances. Successful allocator, valid graphs, defined basis indices and finite active rotation angles are fixture contracts. Zero-duration setup is checked separately from its nonfinite frame path. The existing SDK trigonometric boundary and inherited Matrix infinity specification remain explicit; no physical x87 accuracy, complete skater or playable frame is claimed.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
