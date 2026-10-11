"""Pin exact attachment/component units and the real training-script boundary."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-component-checkpoint.json';proof=p/'particle-component-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-startup-checkpoint.json';assert sha(prior_path)=='ddefdd14a008786799c5dc2ed6b1c3b69407c860ab18a20186e83775f72d6d34';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-component-draft.build.json');module=p/'particle-component-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='3802fc11754cc2c2f759ea135c81153a651a7c1bc3cb1715b978209695031887' and module.stat().st_size==633547
previous=read(p/'particle-startup-browser.json')['suites'];names=['particle-component','particle-component-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-component-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==86
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_component'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(177,334,9,0)
training_result=suites['particle_component_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,46,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-component-original.json');fixture=read(p/'particle-component-fixtures.json');coverage=unit['instruction_coverage'];addresses=['0x476770','0x41f520','0x41da00','0x41e1e0','0x433e70','0x41d740','0x41d760']
assert set(addresses)==set(coverage) and set(addresses)<=set(fixture['functions'])
assert unit['cases']==len(fixture['cases'])==177 and unit['calls']==334 and fixture['float_fields']==[]
assert sum(len(c['steps']) for c in fixture['cases'])==334
missing={k for c in coverage.values() for k in c['missing']};assert missing=={'0x41da4d','0x41da4e','0x41da53','0x41e225','0x41e229','0x41e22b','0x41e232','0x41e235','0x41f6c8'}
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
assert sum(c['covered'] for c in coverage.values())==286 and sum(c['total'] for c in coverage.values())==295
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
training=read(p/'particle-component-training-original.json');tf=read(p/'particle-component-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(45,1,31)
assert len(steps)==46 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap']
assert tf['boundary_factory']==0x41db00 and tf['component_initializer_boundary'] and training['boundary']=='0x41db00'
assert [c['type'] for c in training['components']]==['0x5cb5cb7e','0xc5bceb9e'] and not training['playable']
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:63663/','tab':'160','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-component*'))|{prior_path}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-component-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+7,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+7,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':86,'new_cases':178,'new_calls_including_existing_dependencies':380,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'FlexParticle engine initialization41db00 is an explicit recorded trap. Full particle update/disposal, LockObj update, full Rigidbody Update430e20 and collision response remain unavailable. No complete frame, production rendering or playable game is claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
