"""Pin complete contact assembly after original, Node and browser comparison."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'contact-assembly-checkpoint.json';proof=p/'contact-assembly-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'sphere-query-checkpoint.json'
assert sha(prior_path)=='5b03265a29afd59da183de8a5044a49bc6d2bfcd65f30aaf265f49585e0b18a4'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'contact-assembly-draft.build.json');module=p/'contact-assembly-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='a44f5745b6dcd905574a71e67f975c6891b5e74b6941d487cd000893874a7729'
assert module.stat().st_size==761070
previous=read(p/'sphere-query-browser.json')['suites']
names=['contact-assembly','contact-assembly-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('contact-assembly-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==121
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['contact_assembly'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(1833,1870,1,0)
unit=read(p/'contact-assembly-original.json');fixture=read(p/'contact-assembly-fixtures.json')
assert unit['cases']==len(fixture['cases'])==1833
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1870
coverage=unit['instruction_coverage'];assert set(coverage)=={'0x42c950'}
row=coverage['0x42c950'];assert row['covered']==363 and row['total']==369 and not row['excluded']
assert row['missing']==['0x42ca86','0x42ca8d','0x42cbdb','0x42cc11','0x42cc18','0x42cc19']
assert unit['contact_outcomes']['contacts1/active0/return0']==283
training=read(p/'contact-assembly-training-original.json');tf=read(p/'contact-assembly-training-fixtures.json')
assert suites['contact_assembly_training']['cases']==training['cases']==len(tf['cases'])==95
assert suites['contact_assembly_training']['calls']==training['calls']==sum(len(c['steps']) for c in tf['cases'])==285
assert suites['contact_assembly_training']['nan_fields_classification_only']==0
assert training['counts']=={'thug_rigidbody_rotate_draft':95,'thug_rigidbody_collect_contacts_draft':190}
assert len(training['components'])==len(training['shape_relocations'])==19
assert training['preserved_snapshot_calls']==63 and training['original_collision_objects']==605
assert training['grid_cell_references']==905 and training['grid_nonempty_cells']==73
assert len(training['contact_results'])==95 and training['outcomes']=={'1':55,'0':40}
assert all(row['spheres']==0 and row['auxiliary_contacts']==0 for row in training['components'])
for name,digest in training['source_hashes'].items():assert sha(r/name)==digest==prior['artifact_hashes'][name]
for original,f in [(unit,fixture),(training,tf)]:
 assert original['specimen_sha256']==prior['specimen_sha256'] and not original['heap_events']
 assert f['float_fields']==[] and not f.get('native_callbacks') and not f.get('function_exports')
 assert len(f['globals'])==4604
 for case in f['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*contact-assembly*'))|{prior_path,p/'sphere-query-audit.json',p/'rigidbody-full-inspection.txt'}
for f in paths:
 if f.is_file() and f not in [target,p/'contact-assembly-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':1,'original_addresses':['0x42c950'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+1,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+1,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':121,'new_cases':1833,'new_calls_including_existing_dependencies':1870,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'contact_assembly_training':{**training,'result':'original, Node and actual Chromium comparisons pass'},
 'unrecovered_lifecycle':'Full42c950 contact assembly is recovered with actual cache/probe dependencies and real training prop shapes. Kick42c140, debugdraw42d9d0, full Rigidbody430e20, scene manager45f4a0, skater/input/render/audio and playable original training level remain unfinished. Existing63-call fan training trace is preserved without extension.',
 'coverage_limit':'363/369instructions exercised; two alignment instructions, three conditional reference-cleanup instructions and the point-contact inactive branch remain unexercised. No exclusions or forced callee outputs. All semantic paths retained in C. Earlier checkpoint coverage limits remain unchanged.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
