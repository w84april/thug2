"""Pin verified contact/impact recovery while preserving every prior checkpoint."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-response-checkpoint.json';proof=p/'rigidbody-response-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-dispatch-checkpoint.json';assert sha(prior_path)=='f07492956644f141aa13c3cf73827f45f7218b4a72cff7be1459be23ae5be3d3';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-response-draft.build.json');module=p/'rigidbody-response-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='e89c0e55decfd524be5ef1dc7b284535cb0793bd6d343f63e9c2ce6918749995' and module.stat().st_size==700455
previous=read(p/'particle-dispatch-browser.json')['suites'];names=['rigidbody-response']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-response-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==108
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['rigidbody_response'];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(538,790,10,0)
unit=read(p/'rigidbody-response-original.json');fixture=read(p/'rigidbody-response-fixtures.json');assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==538 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==790
assert fixture['float_fields']==[] and fixture['functions']['0x42cee0']['result']=='wide'
for c in fixture['cases']:
 for step in c['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
coverage=unit['instruction_coverage'];addresses=['0x42cee0','0x42cf90','0x430be0','0x42e980','0x433240','0x47afe0','0x47ac10','0x4680e0','0x48d090'];assert set(addresses)==set(coverage)
assert sum(c['covered'] for c in coverage.values())==907 and sum(c['total'] for c in coverage.values())==911
assert {a for c in coverage.values() for a in c['excluded']}=={'0x42e9cd','0x42e9d2','0x42e9dd','0x42ea0e'}
fan=read(p/'rigidbody-response-fan-script.json');assert sha(r/fan['verified_archived']['path'])==fan['archive']['original_decoded_sha256']=='21c9f93830a0a740bc41e13d81e4ec47adf8e7b33f52235a990ca45231807f87'
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*rigidbody-response*'))|{prior_path,p/'particle-dispatch-audit.json',r/fan['archive']['path']}
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-response-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':9,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+9,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+9,
 'specimen_sha256':prior['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':108,'new_cases':538,'new_calls_including_existing_dependencies':790,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'prior_particle_frame_prefix':prior['prior_particle_frame_prefix'],'particle_frame_prefix':prior['particle_frame_prefix'],'instruction_coverage':coverage,
 'original_only_particle_continuation':prior['original_only_particle_continuation'],
 'original_only_scene_discovery':read(p/'rigidbody-response-scene-discovery.json'),'archived_fan_script':fan,
 'unrecovered_lifecycle':'Full attached-contact constraints, effective mass, collision response and impact script/Sound path are verified independently. Complete Rigidbody430e20 still needs skater kicks42c140, contact detection42c950, contact solver430140 and debug geometry42d9d0. Scene manager45f4a0, full scene script loading, skater/input/render/audio production integration remain unfinished. No complete game frame or playable game claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']+' All finite and generated nonfinite output bits compare exactly. Effective-mass ST0 return uses a raw i64 transport adapter; no additional recovered function count.'}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
