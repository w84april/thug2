"""Pin particle constructors and the real training material-lookup boundary."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-create-checkpoint.json';proof=p/'particle-create-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-engine-checkpoint.json';assert sha(prior_path)=='49a8ccfc90da3f08486047a95ca946372a85fb813f6b0037ccf7343330b7b1c4';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-create-draft.build.json');module=p/'particle-create-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='de1d3635d45fd2dea7f7be38cdd3f2d630ccfed5d4b3e38a798dbeab4d94df95' and module.stat().st_size==642393
previous=read(p/'particle-engine-browser.json')['suites'];names=['particle-create','particle-create-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-create-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==90
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_create'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(263,420,11,0)
training_result=suites['particle_create_training'];assert (training_result['cases'],training_result['calls'],training_result['nan_fields_classification_only'])==(1,47,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-create-original.json');fixture=read(p/'particle-create-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x496d70','0x496f10','0x49b660','0x4d9cf0','0x4d9b80','0x4c21a0','0x497a70','0x496ce0','0x49ac20']
assert set(addresses)|{'0x49ac60'}==set(coverage)
assert unit['cases']==len(fixture['cases'])==263 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==420 and fixture['float_fields']==[]
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
assert sum(c['covered'] for c in coverage.values())==593 and sum(c['total'] for c in coverage.values())==608
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
training=read(p/'particle-create-training-original.json');tf=read(p/'particle-create-training-fixtures.json');steps=tf['cases'][0]['steps']
assert (training['completed_calls'],training['interrupted_calls'],training['completed_startup_objects'])==(46,1,31)
assert len(steps)==47 and sum(bool(s.get('expected_trap')) for s in steps)==1 and steps[-1]['expected_trap']
assert tf['boundary_factory']==0x4d9b80 and tf['component_initializer_boundary'] and training['boundary']=='0x4d9b80'
assert [c['type'] for c in training['components']]==['0x5cb5cb7e','0xc5bceb9e'] and not training['playable']
assert training['effect']['capacity']==70 and training['effect']['flags']=='0x104'
assert training['effect']['material_arguments']==[70,2,0xe9d12353,0x02e58c18,0,0,0]
assert steps[-2]['fn']=='0x49af20' and steps[-2]['result']==training['particle_manager']['address']
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:55021/','tab':'162','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-create*'))|{prior_path,p/'particle-engine-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-create-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':9,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+9,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+9,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':90,'new_cases':264,'new_calls_including_existing_dependencies':467,'new_interrupted_calls':1,
 'actual_training':prior['actual_training'],'particle_frame_prefix':training,'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Nine particle constructor/material/list helpers recovered under the documented allocation contract. The manager49ac60 is verified only with the selected point-sprite factory branch, so is not counted as a complete new routine. Factory4bcef0 and component initializer41db00 remain partial. Actual training stops before material4d9b80 pending shared particle dictionary and texture loading. Unit material tests use explicit dictionary inputs, not a fabricated training texture. Particle setup/update/disposal, LockObj update, full Rigidbody430e20 collision response, skater/input/render/audio remain unavailable. No complete frame or playable game is claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':sorted(set(prior['partial_original_addresses'])|{'0x49ac60','0x4bcef0','0x41db00'}),
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' '+training['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
