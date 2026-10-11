"""Pin full scene sphere queries only after exact original/Node/Chromium checks."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'sphere-query-checkpoint.json';proof=p/'sphere-query-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'sphere-contact-checkpoint.json'
assert sha(prior_path)=='d57b4fa4be5e32c01bf13118af35e39de88eaa73aec22ba947fc3e385155236e'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'sphere-query-draft.build.json');module=p/'sphere-query-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='6625c0ae12e3b1545cef6779c5d353da301d34f4093f19816a10986e17c1a38a'
assert module.stat().st_size==757650
expected=(p/'particle-emission-static-derived.c').read_text().replace('#include <stddef.h>','#include <stddef.h>\n#include "sphere-query-draft.h"').replace('const ThugCollisionMethods thug_static_collision_methods = {','const ThugCollisionMethods thug_static_collision_methods = {\n    .unknown_3c_to_4c={[1]=(uintptr_t)thug_static_collision_sphere_draft},')
assert (p/'sphere-query-static-derived.c').read_text()==expected
previous=read(p/'sphere-contact-browser.json')['suites']
names=['sphere-query','sphere-query-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('sphere-query-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==119
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['sphere_query'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(533,635,4,0)
unit=read(p/'sphere-query-original.json');fixture=read(p/'sphere-query-fixtures.json')
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==533
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==635
coverage=unit['instruction_coverage'];addresses=['0x48c940','0x4110b0','0x410240','0x418300']
assert set(coverage)==set(addresses)
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==560
assert all(not c['excluded'] and not c['missing'] for c in coverage.values())
training=read(p/'sphere-query-training-original.json');tf=read(p/'sphere-query-training-fixtures.json')
assert suites['sphere_query_training']['cases']==training['cases']==len(tf['cases'])==1122
assert suites['sphere_query_training']['calls']==training['calls']==sum(len(c['steps']) for c in tf['cases'])==3366
assert suites['sphere_query_training']['nan_fields_classification_only']==0
assert training['original_collision_objects']==605 and len(training['selected_triangles'])==561
assert training['grid_cell_references']==905 and training['grid_nonempty_cells']==73
assert len(training['relocations'])==978
assert training['cache_candidates_min']==1 and training['cache_candidates_max']==93
assert training['selected_triangles']==prior['sphere_contact_training']['selected_triangles']
assert training['query_outcomes']=={'static/height8.0/result1':510,'grid/height8.0/result1':518,'cache/height8.0/result1':519,
 'static/height32.0/result1':512,'grid/height32.0/result1':519,'cache/height32.0/result1':520,
 'static/height8.0/result0':51,'grid/height8.0/result0':43,'cache/height8.0/result0':42,
 'static/height32.0/result0':49,'grid/height32.0/result0':42,'cache/height32.0/result0':41}
for name,digest in training['source_hashes'].items():assert sha(r/name)==digest==prior['artifact_hashes'][name]
for original,f in [(unit,fixture),(training,tf)]:
 assert original['specimen_sha256']==prior['specimen_sha256'] and not original['heap_events']
 assert f['float_fields']==[] and not f.get('native_callbacks') and not f.get('function_exports')
 assert f['pointer_exports']==[[0x1ff0000,'thug_sphere_query_fixture_state'],[0x645c18,'thug_static_collision_methods']]
 assert len(f['globals'])==3110
 for case in f['cases']:
  for step in case['steps']:
   assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*sphere-query*'))|{prior_path,p/'sphere-contact-audit.json',p/'contact-assembly-inspection.txt'}
for f in paths:
 if f.is_file() and f not in [target,p/'sphere-query-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':4,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+4,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+4,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':119,'new_cases':533,'new_calls_including_existing_dependencies':635,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'sphere_query_training':{**training,'result':'original, Node and actual Chromium comparisons pass'},
 'unrecovered_lifecycle':'Complete static and scene sphere queries4110b0/410240, first-grid48c940 and probe418300 are recovered, including actual training-grid and cache queries. Full contact assembly42c950, Rigidbody, scene manager, skater/input/render/audio and playable original training level remain unfinished. Existing 63-call fan training trace is preserved without extension.',
 'coverage_limit':'All560instructions in the four new bodies exercised, without exclusions. The preceding40e560 helper still has17 documented unexercised defensive instructions; this checkpoint does not change that evidence.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
