"""Pin original/Node/Chromium physics prerequisites without altering earlier work."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-core-checkpoint.json';proof=p/'rigidbody-core-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'level-collision-component-checkpoint.json';assert sha(prior_path)=='75dae3ca0904a2274faa4ab3d2bbd16a6bd9c9e145e671a37f7ffae6e41945d4';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-core-draft.build.json');module=p/'rigidbody-core-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='9ef15fa5add19327835fd4727ef7f4e0b5d3eca9822fd314b6d3a7599342df1e' and module.stat().st_size==617332
previous=read(p/'level-collision-component-browser.json')['suites'];names=['rigidbody-core']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-core-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==80
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
s=suites['rigidbody_core'];assert (s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(567,689,14,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'rigidbody-core-original.json');fixture=read(p/'rigidbody-core-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x403220','0x42e3f0','0x42ef00','0x42e1f0','0x42e310','0x41a730','0x42d4b0','0x42d560','0x42d690','0x42d790','0x42d8a0','0x42ed60','0x42eb10','0x42bd90']
assert set(addresses)==set(coverage)==set(fixture['functions']) and len(addresses)==14
assert unit['cases']==len(fixture['cases'])==567 and unit['calls']==689
assert sum(len(c['steps']) for c in fixture['cases'])==689 and fixture['float_fields']==[]
for c in coverage.values():assert set(c['missing'])==set(c['excluded']) and all('PENDING' not in v for v in c['excluded'].values())
for c in fixture['cases']:
 for step in c['steps']:
  assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
original=read(p/'level-bouncy-startup-exploration.json');assert original['error'] is None and original['completed_calls']==43 and len(original['created_objects'])==31
assert all(o['flags']=='0x60' for o in original['created_objects'])
assert sum(any(c['type']=='0xffb39248' for c in o['components']) for o in original['created_objects'])==19
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:50102/','tab':'156','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('rigidbody-core-*'));paths.update(p.glob('*rigidbody-core*.py'));paths.update(p.glob('*rigidbody-core*.mjs'));paths.add(prior_path)
paths.update(p/name for name in ['explore-level-bouncy-startup.py','level-bouncy-startup-exploration.json','level-bouncy-startup-dependencies.json'])
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-core-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':14,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+14,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+14,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':80,'new_cases':567,'new_calls_including_existing_dependencies':689,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'original_only_next_stage':{'completed_calls':43,'completed_objects':31,'bouncing_objects':19,'recovered_initializer':False},'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Rigidbody initializer42f050, update430e20 and destructor430df0 remain unavailable. Constructor method table exposes only recovered finalize. Previous missing collision/asset lifecycle methods remain unavailable.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
