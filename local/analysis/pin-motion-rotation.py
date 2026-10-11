"""Pin original, Node and observed Chromium fan-rotation comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'motion-rotation-checkpoint.json';proof=p/'motion-rotation-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-response-checkpoint.json';assert sha(prior_path)=='7e96b5daa1aee4b875607fdfd2fc81dce6848d07c191b9bef71f9b947bada3f8';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'motion-rotation-draft.build.json');module=p/'motion-rotation-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='cbf80227a09298c97037925ed790ac3993298300663b31e85b154d7c50b47761' and module.stat().st_size==709961
previous=read(p/'rigidbody-response-browser.json')['suites'];names=['motion-rotation','motion-rotation-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('motion-rotation-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==110
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['motion_rotation'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(621,1275,8,0)
unit=read(p/'motion-rotation-original.json');fixture=read(p/'motion-rotation-fixtures.json');assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==621 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1275
assert fixture['float_fields']==[] and fixture['functions']['0x42bb20']['pointer_args']==[0]
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
coverage=unit['instruction_coverage'];addresses=['0x423f10','0x424b90','0x424d50','0x424f50','0x640e30','0x423130'];assert set(addresses)==set(coverage)
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==722
assert all(not c['missing'] and not c['excluded'] for c in coverage.values())
training=read(p/'motion-rotation-training-original.json');tf=read(p/'motion-rotation-training-fixtures.json')
assert suites['motion_rotation_training']['calls']==training['completed_calls']==len(tf['cases'][0]['steps'])==63
assert not training['interrupted_calls'] and not any(s.get('expected_trap') for c in tf['cases'] for s in c['steps'])
assert len(training['fans'])==len(training['rotation_commands'])==2 and all(len(f['matrices'])==len(set(f['matrices']))==4 for f in training['fans'])
assert training['script_sha256']=='21c9f93830a0a740bc41e13d81e4ec47adf8e7b33f52235a990ca45231807f87'
scene=read(p/'motion-rotation-scene-discovery.json');assert scene['result']=='returned' and not scene['error'] and not scene['boundaries'] and len(scene['object_update_entries'])==32
metadata=read(p/'motion-rotation-descriptors.json');assert len(metadata['table'])==49 and len(metadata['complete_members'])==3 and metadata['unrecovered_members_are_explicit_traps']
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*motion-rotation*'))|{prior_path,p/'rigidbody-response-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'motion-rotation-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
training={**training,'result':'original, Node and actual Chromium comparisons pass'}
checkpoint={**{k:prior[k] for k in ['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix','original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes','checker_dependency_hashes']},
 'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':6,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+6,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+6,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':110,'new_cases':621,'new_calls_including_existing_dependencies':1275,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'fan_training':training,'original_only_scene_discovery':scene,'motion_descriptor_metadata':metadata,
 'unrecovered_lifecycle':'Two fan owners complete four browser updates through original TR_Fan01 and Obj_Rotx. Full Rigidbody430e20, scene manager45f4a0 and45 other registered Motion command bodies remain unfinished. Motion4270e0 path/rail/ballistic branches remain explicit stops. Skater/input/render/audio production integration and playable original training level remain unfinished.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
