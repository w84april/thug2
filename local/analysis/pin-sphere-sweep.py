"""Pin eight complete geometry bodies and original training-edge comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'sphere-sweep-checkpoint.json';proof=p/'sphere-sweep-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'sphere-geometry-checkpoint.json'
assert sha(prior_path)=='97fba453706e6856f238c42c87d73c385df941853adda2386e3a29cbb8699e6f'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'sphere-sweep-draft.build.json');module=p/'sphere-sweep-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='5bb0bedd8f76aadae3a917c3e1780169d4398666293bc1e9da767d26f9c0c007'
assert module.stat().st_size==746302
previous=read(p/'sphere-geometry-browser.json')['suites']
names=['sphere-sweep','sphere-sweep-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('sphere-sweep-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==115
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['sphere_sweep'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(5832,6332,8,0)
unit=read(p/'sphere-sweep-original.json');fixture=read(p/'sphere-sweep-fixtures.json')
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==5832
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==6332
for address in ['0x402640','0x402d60']:assert fixture['functions'][address]['result']=='wide'
coverage=unit['instruction_coverage'];addresses=['0x402640','0x402d60','0x403230','0x4032a0','0x4032e0','0x403330','0x40b610','0x40e280']
assert set(coverage)==set(addresses)
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==1150
assert all(not c['missing'] and not c['excluded'] for c in coverage.values())
training=read(p/'sphere-sweep-training-original.json');tf=read(p/'sphere-sweep-training-fixtures.json')
assert suites['sphere_sweep_training']['cases']==training['cases']==len(tf['cases'])==1683
assert suites['sphere_sweep_training']['calls']==training['calls']==sum(len(c['steps']) for c in tf['cases'])==8415
assert suites['sphere_sweep_training']['nan_fields_classification_only']==0
assert training['original_collision_objects']==605 and training['selected_edges']==561
assert training['outcomes']=={'height0.0/capsule1/intersection1':561,'height8.0/capsule1/intersection1':561,'height32.0/capsule0/intersection0':561}
for pathkey,hashkey in [('loaded_collision','loaded_collision_sha256'),('selection_source','selection_source_sha256')]:
 assert sha(r/training[pathkey])==training[hashkey]==prior['artifact_hashes'][training[pathkey]]
for f in [fixture,tf]:
 assert f['float_fields']==[]
 for case in f['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*sphere-sweep*'))|{prior_path,p/'sphere-geometry-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'sphere-sweep-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+8,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+8,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':115,'new_cases':5832,'new_calls_including_existing_dependencies':6332,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'sphere_sweep_training':{**training,'result':'original, Node and actual Chromium comparisons pass'},
 'unrecovered_lifecycle':'Eight complete segment/capsule and moving-contact helper bodies are verified, including 561 actual training edges. Full swept-sphere40ec90 still needs40e560 and40e940; static sphere dispatch4110b0, scene query410240 and full contact assembly42c950 remain unfinished. Full Rigidbody, scene manager, skater/input/render/audio and playable original training level remain unfinished. Existing 63-call fan training trace is preserved without extension.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
