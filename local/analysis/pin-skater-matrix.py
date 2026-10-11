"""Pin MatrixQueries recovery and preserve all earlier proof without mutation."""
import hashlib,json,struct,zlib
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-matrix-checkpoint.json';assert not target.exists()
prior_path=p/'skater-score-checkpoint.json'
assert sha(prior_path)=='eb6a1a855a18b759cd29d30cc741c5702b5e18dfeab8f7264862785f6c72d2c6'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-matrix-draft.build.json');module=p/'skater-matrix-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='967fd011fdc6945ffce68b434b7ae32060aa982964a6798952fa485691c35b44'
assert module.stat().st_size==801584
previous=read(p/'skater-score-browser.json')['observed']['suites']
names=['skater-matrix']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-matrix-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==133
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-matrix-original.json');fixture=read(p/'skater-matrix-fixtures.json');result=suites['skater_matrix']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(355,557,13,0)
assert unit['cases']==len(fixture['cases'])==355
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==557
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==7
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(422,428)
assert sum(len(row['missing']) for row in coverage.values())==6
assert not any(row['excluded'] for row in coverage.values())
assert all(not row['missing'] for at,row in coverage.items() if at!='0x514430')
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',177,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]+([0xbf518e27] if local else [])
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==row['components'][-2 if local else -1][0] and row['score']['state']!=0
 assert row['next_type']==('0x270f56e1' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
spec=read(p/'skater-matrix-emulator-differences.json')
assert unit['fcos_infinity_specification']==fixture['fcos_infinity_specification']==spec
assert len(spec['cases'])==2 and result['fcos_infinity_cases']==2 and result['fcos_infinity_emulator_differences']==1
for row in spec['cases']:
 step=fixture['cases'][row['case_index']]['steps'][0]
 assert step['fn']=='0x406560' and step['args'][2]==row['angle_bits'] and step['result']==row['raw_emulator_result']
 assert row['adapter_result']==0
assert [(x['angle_bits'],x['raw_emulator_result']) for x in spec['cases']]==[(0x7f800000,1),(0xff800000,0)]
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-matrix-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
name_sources=set()
for key,rows in read(p/'skater-matrix-names.json').items():
 assert rows,key
 for row in rows:
  file=r/row['path'];data=file.read_bytes();raw=row['name'].encode('latin1');name_sources.add(file)
  assert sha(file)==row['sha256']
  assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(key,16))+raw+b'\0'
  assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(key,16)
paths=set(p.glob('*skater-matrix*'))|set((p/'skater-matrix-next-ghidra').rglob('*'))|{prior_path,p/'skater-score-audit.json'}|name_sources
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-matrix-next.txt',p/'skater-matrix-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original comparisons, declared SDK infinity boundary, Node and actual Chromium pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+7,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+7,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':133,'new_cases':355,'new_calls_including_existing_dependencies':557,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'matrix_fcos_infinity_specification':spec,
 'unrecovered_lifecycle':'Local original skater construction creates MatrixQueries and stops before Trick270f56e1; nonlocal850eef66 boundary is unchanged. All eight MatrixQueries commands and its lifecycle are recovered. Trick startup, Score frame/commands/disposal, Input binding, remaining skater assembly, camera, rendering and playable training remain unfinished. Earlier training traces and Score actual-asset initialization are unchanged.',
 'coverage_limit':'422/428 new instructions exercised, with six factory allocation-failure instructions unexercised and no exclusions. The partial582d90 path separately reaches177/463instructions in32 interrupted calls. Only seven complete routines are added to the recovery count. Fixtures use constructed input graphs. Two deliberately infinite-angle helper calls use the declared Intel masked-invalid/SDK boundary, with raw original returns retained and one positive-infinity emulator difference. All other returns and all arena/global/heap bytes compare exactly; zero NaN classification allowances. No physical x87 accuracy or playable-frame claim. Earlier limits remain in immutable previous checkpoints.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
