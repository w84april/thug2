"""Pin particle prerequisites after exact original, Node and Chromium checks."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-startup-checkpoint.json';proof=p/'particle-startup-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-motion-checkpoint.json';assert sha(prior_path)=='4d7002dd1391c69b96b005e353dbde88d63b02c5be566e369a20351533bd7fe2';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-startup-draft.build.json');module=p/'particle-startup-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='1640aed2a1c34a59528aafa38f4e8b7f4c7b1d48c417589a3e2278cd2cd53086' and module.stat().st_size==631298
previous=read(p/'rigidbody-motion-browser.json')['suites'];names=['particle-startup']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-startup-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==84
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_startup'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(182,277,15,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-startup-original.json');fixture=read(p/'particle-startup-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x44a380','0x44be40','0x44a940','0x49a8e0','0x5ae000','0x4607e0','0x4aa2a0','0x4aa6d0','0x4ab130','0x462190','0x4ac120','0x462340','0x460940','0x449540']
assert set(addresses)==set(coverage) and set(addresses)<=set(fixture['functions'])
assert unit['cases']==len(fixture['cases'])==182 and unit['calls']==277
assert sum(len(c['steps']) for c in fixture['cases'])==277 and fixture['float_fields']==[]
missing={k for c in coverage.values() for k in c['missing']}
assert missing=={'0x4ab18a','0x4ab1f2','0x4ab1f6','0x4ac24a','0x4ac24b','0x4ac250','0x4ac254'}
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
assert sum(c['covered'] for c in coverage.values())==689 and sum(c['total'] for c in coverage.values())==696
lzss=read(p/'particle-startup-lzss.json');assert lzss['result']=='pass' and lzss['decoded_sha256']==sha(p/'particle-startup-archived.qb')
exploration=read(p/'particle-startup-frame-exploration.json');assert exploration['result']=='original exploration stopped' and exploration['boundary']['address']=='0x41e1e0'
assert exploration['component_requests']==['0x5cb5cb7e','0xc5bceb9e']
assert all(exploration['particle_native_calls'].get(k) for k in ['0x44a380','0x44be40','0x462340','0x5ae000','0x44a940','0x449540','0x460940','0x41f520','0x4619d0','0x41e1e0'])
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:60556/','tab':'159','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-startup*'))|set(p.glob('*particle-lookup*'))|{prior_path}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-startup-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':14,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+14,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+14,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':84,'new_cases':182,'new_calls_including_existing_dependencies':277,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'first_frame_exploration':{'result':exploration['result'],'boundary':exploration['boundary'],'source':'local/analysis/particle-startup-frame-exploration.json','scope':'Original-only trace passes the new particle script native dependencies and actual LockObj initialization, then stops before FlexParticle factory. No full frame or browser integration of this path is claimed.'},
 'particle_archive':lzss,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'FlexParticle factory, initialization and effects remain unrecovered; LockObj initialization/update remain unavailable in Wasm. Full Rigidbody Update430e20 and collision response remain unavailable. Comparison graphics ports are not production rendering.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
