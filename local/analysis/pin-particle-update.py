"""Pin particle simulation/camera/disposal recovery after original, Node and Chromium checks."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-update-checkpoint.json';proof=p/'particle-update-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'particle-emission-checkpoint.json';assert sha(prior_path)=='5b5b4356a0d02df6bf43daca9e60d6b900a4418936f0f055bd2d89f0d6596769';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-update-draft.build.json');module=p/'particle-update-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='394af137a972a2e2731a6637c2349c4889ca48b4ac46655abc64893da52b36b9' and module.stat().st_size==675878
previous=read(p/'particle-emission-browser.json')['suites'];names=['particle-update','particle-simulation']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-update-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==105
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
coverage={};specimen=None
for name,cases,calls,functions in [('particle-update',428,656,23),('particle-simulation',268,683,7)]:
 result=suites[name.replace('-','_')];assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(cases,calls,functions,0)
 unit=read(p/(name+'-original.json'));fixture=read(p/(name+'-fixtures.json'));specimen=unit['specimen_sha256']
 assert unit['cases']==len(fixture['cases'])==cases and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==calls and fixture['float_fields']==[]
 assert set(coverage).isdisjoint(unit['instruction_coverage']);coverage.update(unit['instruction_coverage'])
 for c in fixture['cases']:
  for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
addresses=['0x4a06d0','0x4a09c0','0x496b40','0x5e1616','0x5bf19f','0x4db570','0x4b2310','0x48c490','0x4d2bd0','0x4d9cd0','0x49ad60','0x498690','0x49b600','0x4c2260','0x4c2af0','0x49b630','0x49ad90','0x49adb0','0x49bb80','0x49bb50','0x49bba0','0x4987f0'];assert set(addresses)==set(coverage)
assert sum(c['covered'] for c in coverage.values())==1072 and sum(c['total'] for c in coverage.values())==1076
for address,c in coverage.items():
 assert c['missing']==(['0x49890a','0x498d98','0x498d9f','0x498e6d'] if address=='0x4987f0' else [])
 assert set(c['excluded'])==set(c['missing'])
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-update*'))|set(p.glob('*particle-simulation*'))|{prior_path,p/'particle-emission-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'particle-update-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':22,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+22,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+22,
 'specimen_sha256':specimen,'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':105,'new_cases':696,'new_calls_including_existing_dependencies':1339,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'particle_frame_prefix':prior['particle_frame_prefix'],'instruction_coverage':coverage,
 'original_only_particle_continuation':prior['original_only_particle_continuation'],
 'unrecovered_lifecycle':'Complete particle engine4987f0, camera selection/culling/distance and particle/material disposal recovered with actual point/buffer/trail methods. Full FlexParticle41df80 and its descriptor registration/dispatch integration remain unfinished. The prior browser training trace is unchanged and stops at41df80. Full Rigidbody response, skater/input/render/audio remain unfinished. No full game frame or playable game claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':'Complete particle simulation, camera/culling and disposal verified with actual game callees, finite valid initialized point/buffer/trail graphs and exact arena/global/return/heap comparisons. Four unreachable simulation alignment instructions excluded. Prior training integration remains unchanged.'}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
