"""Pin complete FlexParticle dispatch and the actual training fire update."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-dispatch-checkpoint.json';proof=p/'particle-dispatch-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-update-checkpoint.json';assert sha(prior_path)=='faac71e50ea5835cd7203ee4cefb8f7f9125c21d43de4eb9e2ab529e31ff52e2';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-dispatch-draft.build.json');module=p/'particle-dispatch-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='a9ff592829897a83f841c45f912abea0cd162197f021f7b12be59ee3fc1dac3e' and module.stat().st_size==680098
previous=read(p/'particle-update-browser.json')['suites'];names=['particle-dispatch','particle-dispatch-training']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-dispatch-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==107
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
for name,cases,calls,functions in [('particle-dispatch',132,283,7),('particle-dispatch-training',1,52,16)]:
 result=suites[name.replace('-','_')];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(cases,calls,functions,0)
 unit=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'))
 assert unit['specimen_sha256']==prior['specimen_sha256']
 assert unit['cases']==len(fixture['cases'])==cases and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==calls
 for c in fixture['cases']:
  for step in c['steps']:
   assert not step.get('expected_trap') and not step.get('quiet_float_fields') and not step.get('global_bit_masks')
   if name=='particle-dispatch':assert not any(step.get(k) for k in ['float_fields','global_float_indices'])
coverage=read(p/'particle-dispatch-original.json')['instruction_coverage']
addresses=['0x642fe0','0x41d6e0','0x41d700','0x41d780','0x41d7f0','0x41d820','0x41d840','0x41d8f0','0x41d920','0x41d940','0x41d960','0x41e190','0x41df80'];assert set(addresses)==set(coverage)
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==501
assert all(not c['missing'] and not c['excluded'] for c in coverage.values())
training=read(p/'particle-dispatch-training-original.json')
assert training['completed_calls']==52 and training['interrupted_calls']==0 and training['barrel_update_complete']
assert training['particle_count']==2 and training['setup_script_after']==0 and training['rate_bits']=='0x43000000' and training['boundaries']==[] and not training['playable']
assert training['completed_startup_objects']==31 and training['effect']['rgba_sha256']==prior['particle_frame_prefix']['effect']['rgba_sha256']
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-dispatch*'))|{prior_path,p/'particle-update-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'particle-dispatch-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':13,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+13,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+13,
 'specimen_sha256':prior['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':107,'new_cases':133,'new_calls_including_existing_dependencies':335,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'prior_particle_frame_prefix':prior['particle_frame_prefix'],'particle_frame_prefix':{**training,'result':'original, Node and actual Chromium comparisons pass'},'instruction_coverage':coverage,
 'original_only_particle_continuation':prior['original_only_particle_continuation'],
 'unrecovered_lifecycle':'Full FlexParticle41df80 and all25 command descriptors now execute with original registration, real command members and particle simulation4987f0. The selected training barrel and fire-owner updates return with two particles emitted and completed setup released. Complete scene-manager updates45f4a0, full Rigidbody response, skater/input/render/audio remain unfinished. No full game frame or playable game claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':'Thirteen complete particle component/descriptor routines verified over501/501 instructions, plus52 completed calls through original training startup and selected barrel/fire updates. Initialized valid finite graphs, exact unit outputs and inherited typed training-global handling. Original flame image and game scripts retained; no substituted game behavior.'}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
