"""Pin motion prerequisites after full original/Node/Chromium agreement."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-motion-checkpoint.json';proof=p/'rigidbody-motion-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-initialize-checkpoint.json';assert sha(prior_path)=='77e2f42c203fb7a0195e910f23964aa08b7d3871b223b8903024bd49b9216fa8';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-motion-draft.build.json');module=p/'rigidbody-motion-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='1b30f9c7b2ffa6d1f51706676f94c96d267950d2eaef852589536b1c56328345' and module.stat().st_size==627253
previous=read(p/'rigidbody-initialize-browser.json')['suites'];names=['rigidbody-motion']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-motion-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==83
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['rigidbody_motion'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(155,327,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'rigidbody-motion-original.json');fixture=read(p/'rigidbody-motion-fixtures.json');coverage=unit['instruction_coverage'];addresses=['0x42be90','0x42bf00','0x42c6d0','0x42c890','0x42e540','0x42ef60','0x430df0']
assert set(addresses)==set(coverage) and set(addresses)<=set(fixture['functions'])
assert unit['cases']==len(fixture['cases'])==155 and unit['calls']==327
assert sum(len(c['steps']) for c in fixture['cases'])==327 and fixture['float_fields']==[]
for c in coverage.values():
 assert set(c['missing'])==set(c['excluded'])
 assert all(reason=='unreachable alignment padding' for reason in c['excluded'].values())
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
assert sum(c['covered'] for c in coverage.values())==739 and sum(c['total'] for c in coverage.values())==741
exploration=read(p/'rigidbody-first-frame-diagnostics.json')
assert exploration['result']=='original exploration stopped' and exploration['diagnostic_calls'][-1]['strings'][1]=='Unknown(0x562fc848)'
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':'http://127.0.0.1:56267/','tab':'158','dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*rigidbody-motion*'));paths.add(prior_path)
paths.update(p/name for name in ['explore-rigidbody-first-frame.py','explore-rigidbody-first-frame-diagnostics.py','rigidbody-first-frame-exploration.json','rigidbody-first-frame-diagnostics.json'])
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-motion-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+7,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+7,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':83,'new_cases':155,'new_calls_including_existing_dependencies':327,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'first_frame_exploration':{'result':exploration['result'],'diagnostic':'CreateFlexibleParticleSystem 0x562fc848 is absent from the isolated script registry; the warning formatter then escapes the configured instruction execution. No full scene frame is claimed.','source':'local/analysis/rigidbody-first-frame-diagnostics.json'},
 'instruction_coverage':coverage,'unrecovered_lifecycle':'Rigidbody Update430e20 remains an explicit trap. Collision response and skater interactions remain unrecovered. Rigidbody dispose430df0 now invokes its real destructor. Other prior missing collision/model/asset lifecycle methods remain unavailable. Comparison graphics ports are not production rendering.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
