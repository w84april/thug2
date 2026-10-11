"""Pin particle image loading and the real training material/reference boundary."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-image-checkpoint.json';proof=p/'particle-image-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-create-checkpoint.json';assert sha(prior_path)=='9c5121ea855cf9958674dae3ad92f371d83b7c9844428933670526d23edacff0';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-image-draft.build.json');module=p/'particle-image-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='1281fa326c522bbeb33c91ed5bf463c9972e07966fbf7f05acf6d1f4945e6a49' and module.stat().st_size==647697
previous=read(p/'particle-create-browser.json')['suites'];names=['particle-image','particle-image-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-image-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==92
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_image'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(154,162,11,0)
training_result=suites['particle_image_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,49,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-image-original.json');fixture=read(p/'particle-image-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x5f45e0','0x5f5af0','0x4e0790','0x4c7f00','0x49f220','0x4c9b00','0x4c7360','0x640c60','0x49f560','0x49f9b0','0x5aa7b0']
assert set(addresses)==set(coverage)
assert unit['cases']==len(fixture['cases'])==154 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==162 and fixture['float_fields']==[]
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
assert sum(c['covered'] for c in coverage.values())==681 and sum(c['total'] for c in coverage.values())==692
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
training=read(p/'particle-image-training-original.json');tf=read(p/'particle-image-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(48,1,31)
assert len(steps)==49 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap']
assert tf['boundary_factory']==0x41dd49 and tf['component_initializer_boundary'] and training['boundary']=='0x41dd49'
assert [c['type'] for c in training['components']]==['0x5cb5cb7e','0xc5bceb9e'] and not training['playable']
assert training['effect']['capacity']==70 and training['effect']['flags']=='0x10105'
assert training['effect']['manager_listed'] and training['effect']['reference']==training['effect']['address']
assert training['effect']['material'] and training['effect']['texture_resource']
assert len(unit['assets'])==7 and all(a['rgba_sha256']==training['effect']['rgba_sha256']=='74c733876c6d540fe0cefaffd0443b18cacb346176cffccd4d70c17e4c1b7b2b' for a in unit['assets'])
assert steps[-2]['fn']=='0x475790' and steps[-3]['fn']=='0x640c60'
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-image*'))|{prior_path,p/'particle-create-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-image-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':11,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+11,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+11,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':92,'new_cases':155,'new_calls_including_existing_dependencies':211,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Eleven image conversion, dictionary, filename and native texture loading routines recovered. The actual training load_level_particle_textures script loads the original flame file, and the barrel-fire material references that decoded resource. PC dictionary/wrapper virtual load slots now bind real implementations; other lifecycle/render slots remain unavailable. Manager49ac60 remains verified only with the point-sprite factory branch. Component initializer41db00 stops at41dd49 before post-creation settings and scripts. Full particle setup/update/disposal, LockObj update, full Rigidbody430e20 collision response, skater/input/render/audio remain unfinished. No complete frame or playable game is claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':sorted(set(prior['partial_original_addresses'])|{'0x49ac60','0x4bcef0','0x41db00'}),
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
