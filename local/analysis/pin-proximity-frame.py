"""Pin proximity queries/events and the next training LockObj boundary."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'proximity-frame-checkpoint.json';proof=p/'proximity-frame-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'motion-frame-checkpoint.json';assert sha(prior_path)=='d28207387c31eaeba2b89ef92428273bbadbedb1f32d48745696b8cc685febd4';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'proximity-frame-draft.build.json');module=p/'proximity-frame-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='9f0f1bcbbb301c87c7abea42ce3533e94da3c26b4dde5d5163ef1a9999c1d076' and module.stat().st_size==656377
previous=read(p/'motion-frame-browser.json')['suites'];names=['proximity-frame','proximity-frame-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('proximity-frame-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==98
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['proximity_frame'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(202,589,9,0)
training_result=suites['proximity_frame_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,49,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'proximity-frame-original.json');fixture=read(p/'proximity-frame-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x55d990','0x5665c0','0x4ec3c0','0x4ec4b0','0x4ec560']
assert set(addresses)==set(coverage)
assert unit['cases']==len(fixture['cases'])==202 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==589 and fixture['float_fields']==[]
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
assert sum(c['covered'] for c in coverage.values())==464 and sum(c['total'] for c in coverage.values())==469
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','global_bit_masks','global_float_indices'])
training=read(p/'proximity-frame-training-original.json');tf=read(p/'proximity-frame-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(48,1,31)
assert len(steps)==49 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap']
assert tf['boundary_factory']==0x41ff90 and tf['component_initializer_boundary'] and tf['boundary_after_script'] and training['boundary']=='0x41ff90'
assert [c['type'] for c in training['components']]==['0x5cb5cb7e','0xc5bceb9e'] and not training['playable']
assert training['effect']['capacity']==70 and training['effect']['flags']=='0x14105'
assert training['effect']['manager_listed'] and training['effect']['reference']==training['effect']['address']
assert training['effect']['material'] and training['effect']['texture_resource']
assert training['effect']['rgba_sha256']=='74c733876c6d540fe0cefaffd0443b18cacb346176cffccd4d70c17e4c1b7b2b'
assert training['particle_scripts']['setup'] and training['particle_scripts']['parameters'] and training['particle_scripts']['instruction'] and training['particle_scripts']['name']=='0xcd1e6836'
assert not training['particle_scripts']['update']
assert all(not s.get('quiet_float_fields') for c in fixture['cases'] for s in c['steps'])
assert training['completed_motion_component'] and training['completed_proximity_component'] and training['lock_component']
assert steps[-2]['fn']=='0x475790' and steps[-3]['fn']=='0x640c60'
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*proximity-frame*'))|{prior_path,p/'motion-frame-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'proximity-frame-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':5,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+5,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+5,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':98,'new_cases':203,'new_calls_including_existing_dependencies':638,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Five complete proximity routines recovered, including indexed player traversal, exact squared distances and real event delivery. Original QB deletion handlers verify owner-state rereads. Actual training barrel Motion and Proximity return; update explicitly stops at LockObj41ff90. Motion4270e0 still partial: path, rail and ballistic modes trap. LockObj, particle updates/disposal, full Rigidbody collision response, skater/input/render/audio remain unfinished. No complete frame or playable game is claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
