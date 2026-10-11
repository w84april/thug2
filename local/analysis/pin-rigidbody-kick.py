"""Pin skater kick only after original, Node and actual browser comparison."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-kick-checkpoint.json';proof=p/'rigidbody-kick-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'contact-assembly-checkpoint.json'
assert sha(prior_path)=='20ab896340b5a4b15db225a0e8a00c53b834a972781b0bbd98d900834a3fe129'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-kick-draft.build.json');module=p/'rigidbody-kick-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='b6b43cbbe1ac977caca2e594628c85e8b1c6177495e135ca4b2c9f9e24a6821a'
assert module.stat().st_size==769991
previous=read(p/'contact-assembly-browser.json')['suites']
names=['rigidbody-kick']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-kick-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==122
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['rigidbody_kick'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(395,407,3,0)
unit=read(p/'rigidbody-kick-original.json');fixture=read(p/'rigidbody-kick-fixtures.json')
assert unit['cases']==len(fixture['cases'])==395
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==407
assert unit['counts']=={'thug_scene_first_ordinary_draft':8,'thug_rigidbody_kick_draft':395,'thug_composite_initialize_draft':4}
coverage=unit['instruction_coverage'];assert set(coverage)=={'0x42c140','0x48c770'}
for address,count in [('0x42c140',402),('0x48c770',29)]:
 row=coverage[address];assert row['covered']==row['total']==count and not row['missing'] and not row['excluded']
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['heap_events']=={'0x5bafc0':57}
assert unit['callees']['0x49e9b0']==12 and unit['callees']['0x4750b0']==4
assert fixture['float_fields']==[] and len(fixture['globals'])==3356
assert len(fixture['native_callbacks'])==17
assert all(x['module']=='prop-sound-audio-callbacks.wasm' for x in fixture['native_callbacks'])
assert [0x4b4630,'thug_model_geometry_enabled_draft'] in fixture['function_exports']
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*rigidbody-kick*'))|{prior_path,p/'contact-assembly-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-kick-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':2,'original_addresses':['0x42c140','0x48c770'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+2,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+2,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':122,'new_cases':395,'new_calls_including_existing_dependencies':407,'new_interrupted_calls':0,
 'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Full skater kick42c140 and first ordinary scene48c770 recovered. Debugdraw42d9d0, full Rigidbody430e20, scene manager45f4a0, skater/input/render/audio and playable original training level remain unfinished. Existing63-call fan training trace preserved without extension.',
 'coverage_limit':'All431instructions in the two new bodies exercised without exclusions. Earlier checkpoint coverage limits remain unchanged. Kick fixtures use initialized ordinary-scene state and original OS audio boundaries; they are not full object updates or production browser audio.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
