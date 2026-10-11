"""Pin original, Node and observed Chromium attachment comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'lock-frame-checkpoint.json';proof=p/'lock-frame-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'proximity-frame-checkpoint.json';assert sha(prior_path)=='39cf7b09aabd820004fc5b5fd4a48882fbb2e767254f46384a7ab76ffef466db';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'lock-frame-draft.build.json');module=p/'lock-frame-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='0228a147c738ccd596a7b5cdd6ae943b1e10f119dafc0d70f342d085de4fb265' and module.stat().st_size==659520
previous=read(p/'proximity-frame-browser.json')['suites'];names=['lock-frame','lock-frame-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('lock-frame-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==100
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['lock_frame'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(294,1125,7,0)
training_result=suites['lock_frame_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,50,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'lock-frame-original.json');fixture=read(p/'lock-frame-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x404100','0x4a2b60','0x4a2c50','0x4a36e0','0x41f760','0x41ff90'];assert set(addresses)==set(coverage)
assert unit['cases']==len(fixture['cases'])==294 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1125 and fixture['float_fields']==[]
assert sum(c['covered'] for c in coverage.values())==702 and sum(c['total'] for c in coverage.values())==703
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
training=read(p/'lock-frame-training-original.json');tf=read(p/'lock-frame-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(49,1,31)
assert len(steps)==50 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap'] and not steps[-2]['expected_trap']
assert training['barrel_update_complete'] and training['boundaries']==['0x41df80'] and steps[-1]['boundary_factory']==0x41df80
assert training['attachment']['entry_count']==training['attachment']['return_count']==2
assert training['attachment']['particle_position'][:3]==training['attachment']['barrel_position'][:3]
assert training['attachment']['particle_position'][3]==3 and training['attachment']['barrel_position'][3]==1
assert tf['component_initializer_boundary'] and tf['boundary_after_script']
assert training['effect']['rgba_sha256']=='74c733876c6d540fe0cefaffd0443b18cacb346176cffccd4d70c17e4c1b7b2b'
assert training['effect']['capacity']==70 and training['effect']['manager_listed'] and training['effect']['reference']==training['effect']['address']
assert training['particle_scripts']['setup'] and training['particle_scripts']['name']=='0xcd1e6836' and not training['particle_scripts']['update']
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*lock-frame*'))|{prior_path,p/'proximity-frame-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'lock-frame-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':6,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+6,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+6,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':100,'new_cases':295,'new_calls_including_existing_dependencies':1175,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Complete LockObj update/wrapper and four bone/matrix dependencies recovered. Actual barrel object update now returns normally; its component at47416736 is Collision(typea432dc41), not Rigidbody; full Rigidbody430e20 remains unrecovered. A second actual object update completes the active fire-effect attachment and explicitly stops at FlexParticle41df80. Motion4270e0 still partial: path, rail and ballistic modes trap. Particle updates/disposal, full Rigidbody collision response, skater/input/render/audio remain unfinished. No full game frame or playable game claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'lookup_correction':'4619f0 ignores its supplied this pointer and uses global6f0fc0; the new source reuses thug_object_find_global, not a direct lookup on component registry6f0fb8.',
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
