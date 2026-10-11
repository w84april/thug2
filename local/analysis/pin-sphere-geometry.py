"""Pin complete sphere primitives and actual training-triangle comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'sphere-geometry-checkpoint.json';proof=p/'sphere-geometry-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-solver-checkpoint.json'
assert sha(prior_path)=='e43ad394e8fff6a68023ffb03e65265407a9adbf93e9a8bb85d28885f58fcf19'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'sphere-geometry-draft.build.json');module=p/'sphere-geometry-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='d7a31d56f01eac707c6494c88fe960777a2a2c4ce06f68c2512270168a0c5be2'
assert module.stat().st_size==734330
previous=read(p/'rigidbody-solver-browser.json')['suites']
names=['sphere-geometry','sphere-geometry-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('sphere-geometry-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==113
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['sphere_geometry']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(2259,2662,4,0)
unit=read(p/'sphere-geometry-original.json');fixture=read(p/'sphere-geometry-fixtures.json')
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==2259
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==2662
assert fixture['functions']['0x40b860']['result']=='wide'
coverage=unit['instruction_coverage'];addresses=['0x403210','0x418330','0x40b860','0x40f9e0']
assert set(coverage)==set(addresses)
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==614
assert all(not c['missing'] and not c['excluded'] for c in coverage.values())
training=read(p/'sphere-geometry-training-original.json');tf=read(p/'sphere-geometry-training-fixtures.json')
assert suites['sphere_geometry_training']['cases']==training['cases']==len(tf['cases'])==1683
assert suites['sphere_geometry_training']['calls']==training['calls']==sum(len(c['steps']) for c in tf['cases'])==8415
assert suites['sphere_geometry_training']['nan_fields_classification_only']==0
assert training['original_collision_objects']==605 and len(training['selected_triangles'])==561
assert len(training['skipped_without_nondegenerate_triangle'])==44
assert len({c['object_index'] for c in training['selected_triangles']})==561
assert training['outcomes']=={'height8.0/result1':560,'height-8.0/result0':561,'height32.0/result0':561,'height8.0/result0':1}
assert sha(r/training['loaded_collision'])==training['loaded_collision_sha256']==prior['artifact_hashes'][training['loaded_collision']]
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
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*sphere-geometry*'))|{prior_path,p/'rigidbody-solver-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'sphere-geometry-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':4,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+4,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+4,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':113,'new_cases':2259,'new_calls_including_existing_dependencies':2662,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'sphere_training':{**training,'result':'original, Node and actual Chromium comparisons pass'},
 'unrecovered_lifecycle':'Point/triangle distance and stationary sphere contact, constructors and original vertex access are verified, including 561 actual training triangles. Swept-sphere40ec90, static sphere dispatch4110b0, scene query410240 and full contact assembly42c950 remain unfinished. Full Rigidbody, scene manager, skater/input/render/audio and playable original training level remain unfinished. Existing 63-call fan training trace is preserved without extension.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
