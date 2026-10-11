"""Pin full swept sphere contacts and actual training-triangle comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'sphere-contact-checkpoint.json';proof=p/'sphere-contact-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'sphere-sweep-checkpoint.json'
assert sha(prior_path)=='bedcfbc99b5fe4a217d0e5083242b58dc37a04f4ffe12ba2871d8e25783c9c25'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'sphere-contact-draft.build.json');module=p/'sphere-contact-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='4dcba20aca73526d32862d41cdd987392aeac48ca0dcc2fa3263826cc07db7fa'
assert module.stat().st_size==754030
previous=read(p/'sphere-sweep-browser.json')['suites']
names=['sphere-contact','sphere-contact-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('sphere-contact-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==117
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['sphere_contact'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(7370,7370,4,0)
unit=read(p/'sphere-contact-original.json');fixture=read(p/'sphere-contact-fixtures.json')
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==7370
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==7370
assert fixture['functions']['0x401020']['pointer_args']==[3]
assert fixture['function_exports']==[[0x5902e0,'thug_segment_initialize'],[0x403210,'thug_sphere_initialize_draft']]
coverage=unit['instruction_coverage'];addresses=['0x401020','0x40e560','0x40e940','0x40ec90']
assert set(coverage)==set(addresses)
assert sum(c['covered'] for c in coverage.values())==1576
assert sum(c['total'] for c in coverage.values())==1593
missing=['0x40e6c3','0x40e6ca','0x40e6d0','0x40e6d2','0x40e6d6','0x40e6dc','0x40e6de','0x40e6e1','0x40e6e3','0x40e6e7','0x40e6ed','0x40e6ef','0x40e6f2','0x40e6f4','0x40e6fb','0x40e6ff','0x40e705']
assert coverage['0x40e560']['missing']==missing
assert coverage['0x40ec90']['covered']==coverage['0x40ec90']['total']==992
assert all(not c['excluded'] and (at=='0x40e560' or not c['missing']) for at,c in coverage.items())
training=read(p/'sphere-contact-training-original.json');tf=read(p/'sphere-contact-training-fixtures.json')
assert suites['sphere_contact_training']['cases']==training['cases']==len(tf['cases'])==2244
assert suites['sphere_contact_training']['calls']==training['calls']==sum(len(c['steps']) for c in tf['cases'])==11220
assert suites['sphere_contact_training']['nan_fields_classification_only']==0
assert training['original_collision_objects']==605 and len(training['selected_triangles'])==561
assert len(training['skipped_without_nondegenerate_triangle'])==44
assert training['outcomes']=={'height32.0/speed-64.0/result1':559,'height8.0/speed-64.0/result1':561,'height-8.0/speed64.0/result1':561,'height32.0/speed64.0/result0':561,'height32.0/speed-64.0/result0':2}
assert sha(r/training['loaded_collision'])==training['loaded_collision_sha256']==prior['artifact_hashes'][training['loaded_collision']]
assert training['selected_triangles']==prior['sphere_training']['selected_triangles']
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
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*sphere-contact*'))|set((p/'sphere-contact-ghidra').rglob('*'))|{prior_path,p/'sphere-sweep-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'sphere-contact-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':4,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+4,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+4,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':117,'new_cases':7370,'new_calls_including_existing_dependencies':7370,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'sphere_contact_training':{**training,'result':'original, Node and actual Chromium comparisons pass'},
 'unrecovered_lifecycle':'Full swept sphere/triangle40ec90 and dependencies40e560/40e940/401020 are recovered and verified, including 561 actual training triangles. Static sphere dispatch4110b0, scene query410240 and full contact assembly42c950 remain unfinished. Full Rigidbody, scene manager, skater/input/render/audio and playable original training level remain unfinished. Existing 63-call fan training trace is preserved without extension.',
 'coverage_limit':'17 defensive parameter-validation instructions in40e560 were not reached; retained in source and included in total coverage. No exclusions or forced callee results. Full40ec90 covers992/992instructions.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
