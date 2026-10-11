"""Pin recovered Input commands and observed browser evidence without changing prior evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'input-command-checkpoint.json';assert not target.exists()
prior_path=p/'input-lifecycle-checkpoint.json'
assert sha(prior_path)=='350f3bd3d27d50d189b601dcda912d100f198140e50bba211b7c3179983720a9'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'input-command-draft.build.json');module=p/'input-command-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='4c3778f7afb4941442b71b63d2dbcd2d03f478251701a647a6b8e4cc8f9864ee'
assert module.stat().st_size==792242
previous=read(p/'input-lifecycle-browser.json')['suites'];names=['input-command']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('input-command-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==129
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
unit=read(p/'input-command-original.json');fixture=read(p/'input-command-fixtures.json');result=suites['input_command']
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'],result['descriptor_rows_verified'])==(856,1090,25,0,15)
assert unit['cases']==len(fixture['cases'])==856
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1090
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==15
assert sum(row['covered'] for row in coverage.values())==sum(row['total'] for row in coverage.values())==339
assert not any(row['excluded'] or row['missing'] for row in coverage.values())
assert unit['initializer_instructions']==82 and unit['table_bytes']==360
assert unit['table_sha256']=='dd883a2591866bb60dfbb6d8a6f6022617c931223fa6cdf8e6e50eda71ba9dd9'
assert len(unit['named_qb_member_dispatches'])==14 and set(unit['named_qb_member_dispatches'].values())=={1}
assert {f'{row["words"][0]:08x}' for row in fixture['descriptor_rows'][:-1]}==set(unit['named_qb_member_dispatches'])
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==1
assert fixture['native_callbacks'][0]['module']=='input-command-diagnostic-fixture.wasm'
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
live=read(p/'input-command-live-keyboard.json')
assert live['result']=='pass' and live['wasm_sha256']==sha(module) and live['unit']==result
assert live['startup']=={'componentCreated':True,'namedCommandsRegistered':14,'tasksRegistered':2,'ownerId':256,'firstSlot':0,'secondSlot':1,'selfSuspended':True}
assert live['cleanup']=={'ownerComponents':0,'firstListEmpty':True,'secondListEmpty':True}
assert len(live['events'])==28 and len(live['commands'])==8 and len(live['actions'])==6
def active(event):
 return [[name,b['held'],b['pressed'],b['released']] for name,b in event['buttons'].items() if b['held'] or b['pressed'] or b['released']]
keys=['Up','Down','Left','Right','X','Square','Circle','Triangle'];masks=[64,128,32,16,1024,2048,512,256]
ids=['5c8faa09','b27804a2','d26adae9','aef7dfd3','b4f2adba','c86fa880','0edbbc2b','c8abf89c','42717176','bbbef674','a93dbbd0','fcfeedbb','b069b600','e5aae06b','7f695a77','7b684919']
for i,event in enumerate(live['events'][:16]):
 assert event['transition']==i+1 and active(event)==[[keys[i//2],*([0,0,1] if i%2 else [1,1,0])]]
 assert event['eventMask']==(0 if i%2 else masks[i//2]) and event['events']==[ids[i]]
 assert event['magnitude']==(127 if i<8 and not i%2 else 0)
command_names=['1090a150','6e24f5fd','56c6c0cd','6df51774','31c6454f','28729460','1090a150','b2a022de']
flags=[(0,0,1),(1,0,1),(0,0,1),(0,1,1),(0,0,1),(0,0,0),(0,0,1),(0,0,1)]
for command,name,expected in zip(live['commands'],command_names,flags):
 assert command['name']==name and command['result']==0
 assert tuple(command[k] for k in ['playerDisabled','networkDisabled','eventsEnabled'])==expected
assert live['commands'][-1]['output']=={'737f15cf':0,'686ad1c2':0,'d6030cea':180,'c94777ac':0}
for i,action in enumerate(live['actions']):
 assert action['command']==live['commands'][i+1] and action['events']==live['events'][16+i*2:18+i*2]
 key=['Up','Up','X','X','Square','Square'][i];mask=[64,64,1024,1024,2048,2048][i]
 for j,event in enumerate(action['events']):
  assert event['transition']==17+i*2+j and event['eventMask']==(0 if j else mask)
  assert active(event)==([] if i in [0,2] else [[key,*([0,0,1] if j else [1,1,0])]])
  assert event['events']==([] if i in [0,2,4] else [ids[[0,0,8,8,10,10][i]+j]])
  assert event['magnitude']==(127 if i==1 and j==0 else 0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
proof=read(p/'input-command-browser.json');assert proof['observed']==candidate
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
fp=fingerprint(candidate)
paths=set(p.glob('*input-command*'))|set((p/'skater-startup-discovery-ghidra').rglob('*'))|{prior_path,p/'input-lifecycle-audit.json',p/'skater-startup-discovery-symbols.tsv'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'input-command-next.txt']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':15,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+15,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+15,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':129,'new_cases':856,'new_calls_including_existing_dependencies':1090,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'live_input_commands':live,'input_command_descriptors':fixture['descriptor_rows'],
 'named_qb_member_dispatches':unit['named_qb_member_dispatches'],
 'unrecovered_lifecycle':'All fourteen Input commands and descriptor registration are recovered. Shared Input startup, both tasks, commands and cleanup run through a generic owner. Full skater scene assembly, camera, rendered frames, production audio/file services and a playable original training level remain unfinished. Prior training traces remain unchanged.',
 'coverage_limit':'All 339 new instructions exercised with no exclusions. Formatter401c30 is an explicit debug-output boundary, retaining arguments and callback ordering. Required HeldLongerThan parameters and valid suppression names are original contracts. SDK trigonometric adapter is not physical x87 validation. Generic owner and initialized platform fixtures are not full skater startup. Prior limitations remain recorded in the immutable previous checkpoint.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fp,'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
