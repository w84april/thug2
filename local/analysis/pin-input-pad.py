"""Pin original controller decoding and the observed browser keyboard bridge."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'input-pad-checkpoint.json';proof=p/'input-pad-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'rigidbody-update-checkpoint.json'
assert sha(prior_path)=='47064fcc1580a4d8162d513ab19e448929e957cb5c50c7d7ca8578c4cdfac74c'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'input-pad-draft.build.json');module=p/'input-pad-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='9b85e1e9a6b697c865f93a518849655ee75ffe852118734ca79d01e3a76f67c4'
assert module.stat().st_size==779318
previous=read(p/'rigidbody-update-browser.json')['suites']
names=['input-pad']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('input-pad-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==126
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['input_pad'];unit=read(p/'input-pad-original.json');fixture=read(p/'input-pad-fixtures.json')
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(971,2197,9,0)
assert unit['cases']==len(fixture['cases'])==971
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==2197
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage']
counts={'0x46b800':9,'0x57b620':3,'0x46b820':47,'0x46b8b0':26,'0x46b940':55,'0x46bb50':66,'0x46bc60':85,'0x46ba80':28,'0x46bda0':356}
assert set(coverage)==set(counts) and sum(counts.values())==675
for address,count in counts.items():
 row=coverage[address];assert row['covered']==row['total']==count and not row['missing'] and not row['excluded']
assert fixture['float_fields']==[] and len(fixture['globals'])==22
assert not fixture.get('native_callbacks') and not fixture.get('memory_adapter')
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
live=read(p/'input-pad-live-keyboard.json')
assert live['result']=='pass' and live['wasm_sha256']==sha(module)
assert len(live['events'])==16
for i,event in enumerate(live['events']):
 name=['Up','Down','Left','Right','X','Square','Circle','Triangle'][i//2]
 assert event['transition']==i+1 and event['active']==[[name,*([0,0,1] if i%2 else [1,1,0])]]
 assert event['magnitude']==(127 if i<8 and not i%2 else 0)
assert (p/'input-pad-keyboard-check.log').read_text().startswith('PASS: keyboard mapping, combinations, repeat, focus loss, hidden page and cleanup')
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
paths=set(p.glob('*input-pad*'))|set((p/'input-pad-ghidra').rglob('*'))|{
 prior_path,p/'rigidbody-update-audit.json',p/'input-component-inspection.txt',r/'src/platform/browser_input.mjs'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'input-pad-next.txt']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
carry=['specimen_sha256','actual_training','prior_particle_frame_prefix','particle_frame_prefix',
 'original_only_particle_continuation','carried_correction','partial_original_addresses','source_hashes',
 'checker_dependency_hashes','fan_training','original_only_scene_discovery','motion_descriptor_metadata',
 'sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training',
 'rigidbody_update_training','rigidbody_active_training']
checkpoint={**{k:prior[k] for k in carry},'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':9,'original_addresses':list(counts),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+9,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+9,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':126,'new_cases':971,'new_calls_including_existing_dependencies':2197,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'live_browser_keyboard':live,
 'platform_source_hashes':{'src/platform/browser_input.mjs':sha(r/'src/platform/browser_input.mjs')},
 'unrecovered_lifecycle':'Complete controller-pad decoding and a focused keyboard packet adapter are verified. Full Input component startup/tasks/event dispatch, skater scene integration, camera, rendered frames, production audio/file services and a playable original training level remain unfinished. The prior67-call scene and2-call active snapshot are preserved unchanged.',
 'coverage_limit':'All675 instructions in nine new bodies exercised without exclusions. The valid four-bit digital direction index is an internal boolean contract. Existing libm atan2 adapter is not physical x87 accuracy. Live keyboard proof uses a dedicated pad in scratch memory, not a started skater or gameplay frame. Earlier checkpoint limits remain unchanged.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
