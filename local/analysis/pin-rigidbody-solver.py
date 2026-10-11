"""Pin contact-solver comparisons against original code, Node and Chromium."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
target=p/'rigidbody-solver-checkpoint.json';proof=p/'rigidbody-solver-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'motion-rotation-checkpoint.json'
assert sha(prior_path)=='b82c1854c59f7d28aafa9ca322e6e6e6aaf62dd8e90542bca06429628c033741'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'rigidbody-solver-draft.build.json');module=p/'rigidbody-solver-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='9e74b3a2c21aa882d272d146e7cc4995c53356a434c9eafb32fc45b7e7f14b49'
assert module.stat().st_size==727753
previous=read(p/'motion-rotation-browser.json')['suites']
names=['rigidbody-solver']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('rigidbody-solver-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==111
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['rigidbody_solver']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(338,418,2,0)
unit=read(p/'rigidbody-solver-original.json');fixture=read(p/'rigidbody-solver-fixtures.json')
assert unit['specimen_sha256']==prior['specimen_sha256']
assert unit['cases']==len(fixture['cases'])==338
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==418
assert fixture['float_fields']==[]
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
coverage=unit['instruction_coverage'];assert set(coverage)=={'0x430140'}
c=coverage['0x430140'];assert (c['covered'],c['total'])==(688,690)
assert set(c['missing'])==set(c['excluded'])=={'0x4301b8','0x4301bf'}
assert set(c['excluded'].values())=={'unreachable alignment padding'}
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
artifacts=dict(prior['artifact_hashes'])
paths=set(p.glob('*rigidbody-solver*'))|{prior_path,p/'motion-rotation-audit.json'}
for f in paths:
 if f.is_file() and f not in [target,p/'rigidbody-solver-next.txt']:
  artifacts[str(f.relative_to(r))]=sha(f)
harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata']
checkpoint={**{k:prior[k] for k in carry},
 'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':1,'original_addresses':['0x430140'],
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+1,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+1,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':111,'new_cases':338,'new_calls_including_existing_dependencies':418,'new_interrupted_calls':0,
 'instruction_coverage':coverage,
 'unrecovered_lifecycle':'Complete contact solver 430140 is verified in isolation with real math, script and Sound dependencies. Full Rigidbody430e20 still requires skater-kick and contact-detection branches. Complete scene manager45f4a0, skater/input/render/audio production integration and playable original training level remain unfinished. Earlier 63-call fan training trace is preserved without extension.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n')
print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
