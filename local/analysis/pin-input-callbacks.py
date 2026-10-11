"""Pin verified device callbacks, real script events and live keyboard evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'input-callbacks-checkpoint.json';proof=p/'input-callbacks-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'input-pad-checkpoint.json'
assert sha(prior_path)=='f27737e9b8a715c46a26dcc86a1f5fe9e6e097ffe2428b10e74019ed96c1db64'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'input-callbacks-draft.build.json');module=p/'input-callbacks-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='ff620f826fafa09d0df91551b36f15bb50daa0718ccb697af1134c4f3c1ce865'
assert module.stat().st_size==781478
previous=read(p/'input-pad-browser.json')['suites'];names=['input-callbacks']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('input-callbacks-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==127
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['input_callbacks'];unit=read(p/'input-callbacks-original.json');fixture=read(p/'input-callbacks-fixtures.json')
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(481,978,8,0)
assert unit['cases']==len(fixture['cases'])==481
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==978
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage']
counts={'0x460820':7,'0x41ebf0':59,'0x41eca0':160,'0x41ef20':111,'0x41f090':38,'0x41f100':32,'0x41f170':6,'0x41f190':6}
assert set(coverage)==set(counts) and sum(counts.values())==419
for address,count in counts.items():
 row=coverage[address];assert row['total']==count and not row['excluded']
 assert row['missing']==(['0x41efed'] if address=='0x41ef20' else [])
assert sum(row['covered'] for row in coverage.values())==418
assert fixture['float_fields']==[] and not fixture.get('native_callbacks')
assert unit['callees']['0x461140']==1748 and unit['callees']['0x473800']==40
assert unit['callees']['0x460470']==6 and unit['callees']['0x475750']==12
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
live=read(p/'input-callbacks-live-keyboard.json')
assert live['result']=='pass' and live['wasm_sha256']==sha(module) and len(live['events'])==16
keys=['Up','Down','Left','Right','X','Square','Circle','Triangle'];masks=[64,128,32,16,1024,2048,512,256]
event_ids=['5c8faa09','b27804a2','d26adae9','aef7dfd3','b4f2adba','c86fa880','0edbbc2b','c8abf89c',
 '42717176','bbbef674','a93dbbd0','fcfeedbb','b069b600','e5aae06b','7f695a77','7b684919']
for i,event in enumerate(live['events']):
 assert event['transition']==i+1 and event['active']==[[keys[i//2],*([0,0,1] if i%2 else [1,1,0])]]
 assert event['eventMask']==(0 if i%2 else masks[i//2]) and event['events']==[event_ids[i]]
 assert event['magnitude']==(127 if i<8 and not i%2 else 0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':{'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':5}},indent=2)+'\n')
paths=set(p.glob('*input-callbacks*'))|set(p.glob('*input-component*'))|set((p/'input-component-ghidra').rglob('*'))|{
 prior_path,p/'input-pad-audit.json',p/'input-component-core-inspection.txt',p/'input-component-task-inspection.txt',p/'input-component-ghidra.log'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'input-callbacks-next.txt']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':8,'original_addresses':list(counts),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+8,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+8,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':127,'new_cases':481,'new_calls_including_existing_dependencies':978,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'live_input_callbacks':live,
 'unrecovered_lifecycle':'Input packet callbacks, targeted button events and UI blocking are recovered. Device task allocation/registration/lifetime, Input initialization and command descriptors, skater scene integration, camera, rendered frames, production audio/file services and a playable original training level remain unfinished. The prior67-call scene and2-call active snapshot are unchanged.',
 'coverage_limit':'418 of419 instructions covered; allocation-failure41efed remains unexercised, with no exclusions. Modal UI56a1eae3 must provide checksumcdc00e63; otherwise the original reads an uninitialized stack slot and this port traps. Browser proof uses synthetic component/task/registry state and actual original callbacks/events/decoder. Earlier limits remain unchanged.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':read(proof)['dom_fingerprint'],'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
