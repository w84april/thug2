"""Pin complete prop/manager updates after original, Node and Chromium checks."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-update-checkpoint.json';proof=p/'rigidbody-update-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-kick-checkpoint.json'
assert sha(prior_path)=='bd38523d4810d6a69450b56b83b487b3a274ba3c61b77b3df4b8e8f196db1a9c'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-update-draft.build.json');module=p/'rigidbody-update-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():
 assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='f98c6facf3c3ca5f1d0934b0a80bab8c81e1c755fc46ac0c9075323a765f18a1'
assert module.stat().st_size==775781
oldinit=p/'lock-frame-rigidbody-initialize-derived.c'
assert (p/'rigidbody-update-initialize-derived.c').read_text()==oldinit.read_text().replace('thug_lock_rigidbody_boundary_draft','thug_rigidbody_update_draft')
assert str(p/'rigidbody-update-core-derived.c') in build['command']
assert str(p/'lock-frame-rigidbody-core-derived.c') not in build['command']
previous=read(p/'rigidbody-kick-browser.json')['suites']
names=['rigidbody-update','rigidbody-update-training','rigidbody-update-active-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-update-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==125
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['rigidbody_update']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(455,871,5,0)
unit=read(p/'rigidbody-update-original.json');fixture=read(p/'rigidbody-update-fixtures.json')
assert unit['cases']==len(fixture['cases'])==455
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==871
assert unit['counts']==result['counts']=={'thug_rigidbody_update_draft':657,'thug_object_manager_add':114,'thug_composite_initialize_draft':8,'thug_rigidbody_debug_draw_draft':60,'thug_composite_manager_update_draft':32}
coverage=unit['instruction_coverage'];assert set(coverage)=={'0x430e20','0x42d9d0','0x45f4a0'}
assert coverage['0x430e20']=={'covered':277,'total':286,'missing':['0x430f18','0x430f1f','0x4310f1','0x4310f8','0x4310f9','0x4310fe','0x43112c','0x431133','0x431134'],'excluded':{}}
for address,count in [('0x42d9d0',196),('0x45f4a0',112)]:
 row=coverage[address];assert row['covered']==row['total']==count and not row['missing'] and not row['excluded']
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['heap_events']=={'0x5bafc0':119,'0x5baba0':28}
assert fixture['float_fields']==[] and len(fixture['globals'])==7961
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
training=read(p/'rigidbody-update-training-original.json')
active=read(p/'rigidbody-update-active-training-original.json')
for name,report,calls,manager,objects,rigid in [
 ('rigidbody-update-training',training,67,4,128,76),
 ('rigidbody-update-active-training',active,2,2,64,38)]:
 f=read(p/(name+'-fixtures.json'));s=suites[name.replace('-','_')]
 assert s['cases']==report['cases']==len(f['cases'])==1
 assert s['calls']==report['calls']==report['completed_calls']==calls
 assert report['interrupted_calls']==s['nan_fields_classification_only']==0
 assert report['full_manager_updates']==manager and report['object_updates']==objects and report['rigidbody_updates']==rigid
 assert report['specimen_sha256']==prior['specimen_sha256'] and not report['playable']
 steps=f['cases'][0]['steps'];assert len(steps)==calls
 full=[step for step in steps if step['fn']=='0x45f4a0'];assert len(full)==manager
 assert all(step['args']==[0x6f00000,0] and not step.get('expected_trap') for step in full)
 assert [0x6f00000,'thug_sphere_query_fixture_state'] in f['pointer_exports']
 assert f['functions']['0x45f4a0']['stack_args']==[]
assert training['preserved_prefix_calls']==63 and len(training['frames'])==4
assert all(len(f['objects'])==32 and len(f['rigidbodies'])==19 for f in training['frames'])
assert all(body['mode']==0 for f in training['frames'] for body in f['rigidbodies'])
assert training['dependency_calls']=={'0x42c140':76,'0x4270e0':48,'0x41df80':4}
assert active['snapshot_prefix_calls']==67 and len(active['frames'])==2
assert len(active['initial_props'])==len(active['wake_input'])==19
assert active['wake_input']==[[prop['component']+0x10c,'01000000'] for prop in active['initial_props']]
assert active['wake_input']==read(p/'rigidbody-update-active-training-fixtures.json')['cases'][0]['patches']
assert active['dependency_calls']=={'0x42c140':38,'0x42bf00':26,'0x42c950':26,'0x430140':17,'0x4270e0':24,'0x41df80':2}
for frame,settled,contacts in zip(active['frames'],[12,13],[56,60]):
 assert frame['object_updates']==32 and frame['rigidbody_updates']==19
 assert sum(prop['mode']==0 for prop in frame['props'])==settled
 assert sum(prop['contact_count'] for prop in frame['props'])==contacts
 assert all(prop['component']==before['component'] and prop['position'][:3]!=before['position'][:3] for prop,before in zip(frame['props'],active['initial_props']))
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes'])
paths=set(p.glob('*rigidbody-update*'))|{prior_path,p/'rigidbody-kick-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-update-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata',
 'sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':3,'original_addresses':['0x430e20','0x42d9d0','0x45f4a0'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+3,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+3,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':125,'new_cases':455,'new_calls_including_existing_dependencies':871,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'rigidbody_update_training':training,'rigidbody_active_training':active,
 'unrecovered_lifecycle':'Full Rigidbody430e20, debug traversal42d9d0 and scene manager45f4a0 recovered and wired. Original training startup now continues through four complete manager passes; two further passes from a snapshot explicitly wake19 props. Skater/input, rendered frames, production graphics/audio/file services and a playable original training level remain unfinished. Historical coverage limits remain.',
 'coverage_limit':'585/594 instructions exercised, no exclusions. Nine430e20 instructions unexercised: two alignment instructions and seven conditional local-probe-reference unlink instructions. Debug graphics5480a0 is an original bare RET; traversal verification does not establish rendering. Training fixtures retain prior file/GPU/audio service boundaries and the active case uses explicit mode-only wake input.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n')
print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
