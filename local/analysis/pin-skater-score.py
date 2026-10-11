"""Pin recovered Score startup, actual asset initialization and browser evidence."""
import hashlib,json,struct,zlib
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'skater-score-checkpoint.json';assert not target.exists()
prior_path=p/'skater-construction-checkpoint.json'
assert sha(prior_path)=='35a6d5b37ce804adcf7ee38009f5fe9ee2ed6140910ec7e64336171a1138af27'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'skater-score-draft.build.json');module=p/'skater-score-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='8f40960a253154d68213a1e782c5a6d7e09f9f46142a3f691f4519cabdbd733c'
assert module.stat().st_size==798271
previous=read(p/'skater-construction-browser.json')['observed']['suites']
names=['skater-score','skater-score-assets']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('skater-score-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==132
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'skater-score-original.json');fixture=read(p/'skater-score-fixtures.json');result=suites['skater_score']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(268,484,9,0)
assert unit['cases']==len(fixture['cases'])==268
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==484
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==7
assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(301,311)
assert sum(len(row['missing']) for row in coverage.values())==10
assert not any(row['excluded'] for row in coverage.values())
prefix=unit['partial_constructor']
assert (prefix['address'],prefix['covered'],prefix['total'],prefix['boundary'],prefix['interrupted_calls'])==('0x582d90',169,463,'0x45ee20',32)
assert len(prefix['records'])==32 and prefix['address'] not in coverage
for row in prefix['records']:
 local=row['arguments'][2]&255
 assert [t for _,t in row['components']]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local else [])+[0xd262802f]
 assert row['boundary'][0]==0x45ee20 and row['boundary'][3]==1
 assert row['score']['component']==row['components'][-1][0] and row['score']['state']!=0
 assert row['next_type']==('0xbf518e27' if local else '0x850eef66')
assert sum(row['diagnostics_mutate_id'] for row in prefix['records'])==16
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['direct_initializer_prefix'] and fixture['boundary_factory']==0x45ee20
interrupted=[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
  if step.get('expected_trap'):interrupted.append(step)
assert len(interrupted)==32 and all(step['fn']=='0x582d90' for step in interrupted)
assets=read(p/'skater-score-assets-original.json');af=read(p/'skater-score-assets-fixtures.json');ar=suites['skater_score_assets']
assert (ar['cases'],ar['calls'],ar['functions'],ar['nan_fields_classification_only'])==(4,12,2,0)
assert assets['cases']==len(af['cases'])==4 and assets['calls']==12
assert assets['counts']==ar['counts']=={'thug_script_load_qb':8,'thug_score_construct_draft':4}
assert assets['specimen_sha256']==prior['specimen_sha256']
for source in assets['sources']:
 assert sha(r/source['path'])==source['sha256'] and (r/source['path']).stat().st_size==source['bytes']
assert len(assets['sources'])==2 and len(assets['records'])==4
assert [row['positions_field'] for row in assets['records']]==['0xf314312a','0x44e39bb5','0xbeeca6d6','0xf314312a']
for row in assets['records']:
 assert row['curve_count']==7 and len(row['curve'])==8 and row['curve'][-1]==row['curve'][-2]
 assert row['number_bits']=='0x41700000' and row['integer_word']=='0x3' and row['debug']==0 and row['step_bits']=='0x3e124925'
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'skater-score-browser.json');assert proof['observed']==candidate and proof['status'].startswith('PASS')
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
name_sources=set()
for key,rows in read(p/'skater-score-names-discovery.json').items():
 assert rows,key
 for row in rows:
  file=r/row['path'];data=file.read_bytes();raw=row['name'].encode('latin1');name_sources.add(file)
  assert sha(file)==row['sha256']
  assert data[row['offset']:row['offset']+len(raw)+6]==b'\x2b'+struct.pack('<I',int(key,16))+raw+b'\0'
  assert zlib.crc32(raw.lower().replace(b'/',b'\\'))^0xffffffff==int(key,16)
paths=set(p.glob('*skater-score*'))|set(p.glob('skater-next-components-*'))|set((p/'skater-next-components-ghidra').rglob('*'))|{prior_path,p/'skater-construction-audit.json'}|{r/row['path'] for row in assets['sources']}|name_sources
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'skater-score-next.txt',p/'skater-score-audit.json']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+7,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+7,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':132,'new_cases':272,'new_calls_including_existing_dependencies':496,'new_interrupted_calls':32,
 'instruction_coverage':coverage,'prior_skater_constructor_prefix':prior['skater_constructor_prefix'],'skater_constructor_prefix':prefix,
 'score_asset_initialization':assets,
 'unrecovered_lifecycle':'The actual skater constructor creates Score and stores its component and player ID, then stops before SkaterMatrixQueries or SkaterNonLocalNetLogic. Original physics.qb and panelstuff.qb also initialize Score through the recovered loader. Score disposal/frame/commands, Input binding, remaining skater assembly, camera, rendering and playable training remain unfinished. Earlier training scene traces are unchanged.',
 'coverage_limit':'301/311 new instructions exercised with no exclusions:three unreachable alignment instructions and seven allocation-failure instructions unexercised. The partial582d90 path separately reaches169/463instructions in32 interrupted calls. Seven complete routines only are added to the recovery count. Unit configuration graphs are explicit input; the separate actual-asset suite executes the original whole-file loader on two original QB files. Score output is exact; parser scratch retains existing typed NaN handling, with no classified NaNs observed. Pending Score methods explicitly trap. Earlier limits remain in the immutable prior checkpoint.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fingerprint(candidate),'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
