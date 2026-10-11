"""Pin complete particle initialization and the next actual training Motion boundary."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-setup-checkpoint.json';proof=p/'particle-setup-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-image-checkpoint.json';assert sha(prior_path)=='0da058d63594cf0470df66183c1939b25e50190bb86fabb027a07aa51f399d62';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-setup-draft.build.json');module=p/'particle-setup-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='962c8000a7023ab5e93611b4cad89d1c3a7881cd9f83b3647f2f5a644f10eb26' and module.stat().st_size==650076
previous=read(p/'particle-image-browser.json')['suites'];names=['particle-setup','particle-setup-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-setup-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==94
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_setup'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(99,366,5,0)
training_result=suites['particle_setup_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,49,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-setup-original.json');fixture=read(p/'particle-setup-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x497790','0x497900','0x41db00']
assert set(addresses)==set(coverage)
assert unit['cases']==len(fixture['cases'])==99 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==366 and fixture['float_fields']==[]
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
assert sum(c['covered'] for c in coverage.values())==554 and sum(c['total'] for c in coverage.values())==562
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','global_bit_masks','global_float_indices'])
training=read(p/'particle-setup-training-original.json');tf=read(p/'particle-setup-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(48,1,31)
assert len(steps)==49 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap']
assert tf['boundary_factory']==0x4270e0 and tf['component_initializer_boundary'] and tf['boundary_after_script'] and training['boundary']=='0x4270e0'
assert [c['type'] for c in training['components']]==['0x5cb5cb7e','0xc5bceb9e'] and not training['playable']
assert training['effect']['capacity']==70 and training['effect']['flags']=='0x14105'
assert training['effect']['manager_listed'] and training['effect']['reference']==training['effect']['address']
assert training['effect']['material'] and training['effect']['texture_resource']
assert training['effect']['rgba_sha256']=='74c733876c6d540fe0cefaffd0443b18cacb346176cffccd4d70c17e4c1b7b2b'
assert training['particle_scripts']['setup'] and training['particle_scripts']['parameters'] and training['particle_scripts']['instruction'] and training['particle_scripts']['name']=='0xcd1e6836'
assert not training['particle_scripts']['update']
assert unit_result['signaling_nan_words_quieted_per_x87']==2
assert coverage['0x41db00']['covered']==coverage['0x41db00']['total']==356
for c in fixture['cases']:
 for step in c['steps']:
  if step.get('quiet_float_fields'):assert step['fn']=='0x41db00' and step['quiet_float_fields']==[0x19a0044,0x19a0048]
assert steps[-2]['fn']=='0x475790' and steps[-3]['fn']=='0x640c60'
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-setup*'))|{prior_path,p/'particle-image-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-setup-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':3,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+3,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+3,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':94,'new_cases':100,'new_calls_including_existing_dependencies':415,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Complete FlexParticle initializer and two persistent script setup/clear routines recovered. Real training startup creates and finalizes the particle owner, its70-point effect, original flame material and persistent emit script. Startup script returns; barrel frame explicitly stops at unrecovered Motion4270e0. Only point-sprite creation is available; other particle factories still trap. Motion, Proximity and LockObj updates, particle component/engine updates and disposal, full Rigidbody430e20 collision response, skater/input/render/audio remain unfinished. No complete frame or playable game is claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':sorted((set(prior['partial_original_addresses'])-{'0x41db00'})|{'0x49ac60','0x4bcef0'}),
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
