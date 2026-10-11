"""Pin recovered particle prerequisites after Node and observed Chromium checks."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'particle-frame-checkpoint.json';proof=p/'particle-frame-browser.json';assert not target.exists() and not proof.exists()
prior_path=p/'lock-frame-checkpoint.json';assert sha(prior_path)=='55406554943e67ae350c75951e1fe6e253e494d2db283402e473f897e4281968';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'particle-frame-draft.build.json');module=p/'particle-frame-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='ece0d20a4701d56ed462228c23c1587bb7ddb5a50b7e8a222ae3ff5631042f47' and module.stat().st_size==660810
previous=read(p/'lock-frame-browser.json')['suites'];names=['particle-frame']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('particle-frame-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==101
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit_result=suites['particle_frame'];assert (unit_result['cases'],unit_result['calls'],unit_result['functions'],unit_result['nan_fields_classification_only'])==(246,906,10,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'particle-frame-original.json');fixture=read(p/'particle-frame-fixtures.json');coverage=unit['instruction_coverage']
addresses=['0x433e90','0x433ea0','0x496f60','0x497ab0','0x496970','0x4969b0','0x496c30'];assert set(addresses)==set(coverage)
assert unit['cases']==len(fixture['cases'])==246 and unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==906 and fixture['float_fields']==[]
assert sum(c['covered'] for c in coverage.values())==sum(c['total'] for c in coverage.values())==197
for c in coverage.values():assert not c['missing'] and not c['excluded']
for c in fixture['cases']:
 for step in c['steps']:assert not any(step.get(k) for k in ['expected_trap','float_fields','quiet_float_fields','global_bit_masks','global_float_indices'])
reference=read(p/'particle-frame-continuation.json');discovery=read(p/'particle-frame-discovery.json')
assert reference['result']=='returned' and reference['eip']=='0x7f00000' and reference['stack_pointer']=='0x7018004'
assert reference['particle_count']==2 and reference['setup_script']==0 and reference['rate_bits']=='0x43000000'
assert discovery['boundary']=='0x497b00' and discovery['stack'][1]=='0x8ffdef38'
assert reference['effect']==discovery['receiver']==discovery['effect']['address']
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes']);paths=set(p.glob('*particle-frame*'))|{prior_path,p/'lock-frame-audit.json'}
for directory in list(paths):
 if directory.is_dir():paths.update(directory.rglob('*'))
for f in paths:
 if f.is_file() and f not in [target,p/'particle-frame-next.txt']:artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={'result':'original, Node and actual Chromium comparisons pass; unpromoted','prior_checkpoint_sha256':sha(prior_path),'new_functions':7,'original_addresses':addresses,
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+7,'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+7,
 'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),'browser_suites':101,'new_cases':246,'new_calls_including_existing_dependencies':906,'new_interrupted_calls':0,
 'actual_training':prior['actual_training'],'particle_frame_prefix':prior['particle_frame_prefix'],'instruction_coverage':coverage,
 'original_only_particle_continuation':reference,
 'unrecovered_lifecycle':'Seven particle update prerequisites recovered, including actual retained script execution/cleanup. The full FlexParticle41df80 and engine4987f0 frame are still unrecovered. The prior verified training object trace remains unchanged and stops at41df80. Original-only discovery of component command registration is separate evidence, not browser integration. Particle command dispatch, emission, disposal, full Rigidbody response, skater/input/render/audio remain unfinished. No full game frame or playable game claimed.',
 'carried_correction':prior['carried_correction'],'partial_original_addresses':prior['partial_original_addresses'],
 'source_hashes':prior['source_hashes'],'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':read(proof)['dom_fingerprint'],
 'playable':False,'scope':unit['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
