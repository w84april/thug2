"""Pin complete prop startup only after original/Node/Chromium agreement."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-initialize-checkpoint.json';proof=p/'rigidbody-initialize-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-core-checkpoint.json';assert sha(prior_path)=='3a6c0156570e8720fd881a39dace80d8e7e4afd656fa8bdce28c27ddc727a400';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-initialize-draft.build.json');module=p/'rigidbody-initialize-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='4db9bb10adca32e5e16a01daf05ff60e010423ea0ce0e3a8ea1613e1538f3aa5' and module.stat().st_size==623978
previous=read(p/'rigidbody-core-browser.json')['suites'];names=['rigidbody-initialize','rigidbody-initialize-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-initialize-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==82
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['rigidbody_initialize'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(130,382,5,0)
training_result=suites['rigidbody_initialize_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,43,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'rigidbody-initialize-original.json');fixture=read(p/'rigidbody-initialize-fixtures.json');coverage=unit['instruction_coverage'];addresses=['0x42f050','0x477010','0x468b60']
assert set(addresses)==set(coverage) and set(addresses)<=set(fixture['functions'])
assert unit['cases']==len(fixture['cases'])==130 and unit['calls']==382
assert sum(len(c['steps']) for c in fixture['cases'])==382 and fixture['float_fields']==[]
for c in coverage.values():
 assert set(c['missing'])==set(c['excluded'])
 assert not any('UNREVIEWED' in v or 'PENDING' in v for v in c['excluded'].values())
for name in ['rigidbody-initialize','rigidbody-initialize-training']:
 f=read(p/(name+'-fixtures.json'))
 for c in f['cases']:
  for step in c['steps']:
   assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks'])
actual=read(p/'rigidbody-initialize-training-original.json')
assert actual['completed_calls']==43 and actual['completed_objects']==31 and actual['components']==172
assert actual['bouncing_objects']==19 and actual['ordinary_objects']==12 and actual['unavailable_bouncing_objects']==[]
assert actual['objects'][:12]==prior['actual_training']['objects']
assert all(o['flags']==0x60 and o['complete'] for o in actual['objects'])
assert len(actual['rigidbodies'])==19 and actual['visible_geometry_clones']==29
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:53090/','tab':'157','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*rigidbody-initialize*'));paths.add(prior_path)
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-initialize-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':3,'original_addresses':addresses,'newly_completed_prior_partial':['0x468ec0'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+3,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+3,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':82,'new_cases':131,'new_calls_including_existing_dependencies':425,'new_interrupted_calls':0,
 'actual_training':{**actual,'result':'original, Node and Chromium startup comparison pass'},'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Rigidbody update430e20 and destructor430df0 remain explicit traps. Previous missing collision/asset lifecycle methods remain unavailable. Startup comparison ports are not production rendering.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':[a for a in prior['partial_original_addresses'] if a!='0x468ec0'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
