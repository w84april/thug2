"""Pin original Input lifecycle, Node regression and actual browser evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'input-lifecycle-checkpoint.json';proof=p/'input-lifecycle-browser.json'
assert not target.exists() and not proof.exists()
prior_path=p/'input-callbacks-checkpoint.json'
assert sha(prior_path)=='162fb8f42620ae53976c9144123ae006149a4fd90983005041f6aa841174cb26'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'input-lifecycle-draft.build.json');module=p/'input-lifecycle-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='98e9e6ecbfb4ca33aa27d5f62dc64fa00cc5408995619065f62d2c3037b60908'
assert module.stat().st_size==789004
previous=read(p/'input-callbacks-browser.json')['suites'];names=['input-lifecycle']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('input-lifecycle-checkpoint-'+n+'-result.json')) for n in names}
assert len(suites)==128
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
result=suites['input_lifecycle'];unit=read(p/'input-lifecycle-original.json');fixture=read(p/'input-lifecycle-fixtures.json')
assert (result['cases'],result['calls'],result['functions'],result['nan_fields_classification_only'])==(460,1252,34,0)
assert unit['cases']==len(fixture['cases'])==460
assert unit['calls']==sum(len(c['steps']) for c in fixture['cases'])==1252
assert unit['counts']==result['counts'] and unit['specimen_sha256']==prior['specimen_sha256']
coverage=unit['instruction_coverage'];assert len(coverage)==28
assert sum(row['covered'] for row in coverage.values())==700 and sum(row['total'] for row in coverage.values())==707
assert not any(row['excluded'] for row in coverage.values())
assert [x for row in coverage.values() for x in row['missing']]==['0x41f223','0x41f2a0','0x41ef08','0x41ef0c','0x41ef0e','0x41ef15','0x41ef18']
assert fixture['float_fields']==[] and len(fixture['native_callbacks'])==2
for callback in fixture['native_callbacks']:assert callback['module']=='input-lifecycle-hardware-fixture.wasm'
for case in fixture['cases']:
 for step in case['steps']:
  assert not any(step.get(k) for k in ['expected_trap','quiet_float_fields','global_bit_masks','float_fields','global_float_indices'])
def fingerprint(value):
 canonical=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
 for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
 return {'fnv1a64':f'{h:016x}','canonical_characters':len(canonical),'top_level_keys':len(value)}
live=read(p/'input-lifecycle-live-keyboard.json')
assert live['result']=='pass' and live['wasm_sha256']==sha(module) and len(live['events'])==16
assert live['startup']=={'componentCreated':True,'tasksRegistered':2,'ownerId':256,'firstSlot':0,'secondSlot':1,'selfSuspended':True}
assert live['cleanup']=={'ownerComponents':0,'firstListEmpty':True,'secondListEmpty':True}
assert live['unit_dom_fingerprint']==fingerprint(result)
keys=['Up','Down','Left','Right','X','Square','Circle','Triangle'];masks=[64,128,32,16,1024,2048,512,256]
ids=['5c8faa09','b27804a2','d26adae9','aef7dfd3','b4f2adba','c86fa880','0edbbc2b','c8abf89c','42717176','bbbef674','a93dbbd0','fcfeedbb','b069b600','e5aae06b','7f695a77','7b684919']
for i,event in enumerate(live['events']):
 assert event['transition']==i+1 and event['active']==[[keys[i//2],*([0,0,1] if i%2 else [1,1,0])]]
 assert event['eventMask']==(0 if i%2 else masks[i//2]) and event['events']==[ids[i]]
 assert event['magnitude']==(127 if i<8 and not i%2 else 0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
fp=fingerprint(candidate)
assert sys.argv[1]==fp['fnv1a64'] and int(sys.argv[2])==fp['canonical_characters'] and int(sys.argv[3])==fp['top_level_keys']==5
proof.write_text(json.dumps({**candidate,'browser':'Codex in-app Chromium','url':sys.argv[4],'tab':sys.argv[5],
 'dom_fingerprint':fp,'unit_recheck':live['unit_dom_fingerprint'],
 'unit_recheck_reason':'Shared-owner fixture moved its allocating ID assignment after component creation; current fixture reran in the live page after the full regression page started.'},indent=2)+'\n')
paths=set(p.glob('*input-lifecycle*'))|set((p/'input-lifecycle-ghidra').rglob('*'))|{prior_path,p/'input-callbacks-audit.json'}
artifacts=dict(prior['artifact_hashes']);harnesses=dict(prior['harness_hashes'])
for f in paths:
 if f.is_file() and f not in [target,p/'input-lifecycle-next.txt']:
  artifacts[str(f.relative_to(r))]=sha(f)
  if f.suffix in ['.py','.mjs']:harnesses[str(f.relative_to(r))]=sha(f)
checkpoint={**prior,'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'prior_checkpoint_sha256':sha(prior_path),'new_functions':28,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':prior['unpromoted_functions_in_this_module']+28,
 'unpromoted_functions_across_separate_experiments':prior['unpromoted_functions_across_separate_experiments']+28,
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':sha(r/'local/build/thug-core.wasm'),
 'browser_suites':128,'new_cases':460,'new_calls_including_existing_dependencies':1252,'new_interrupted_calls':0,
 'instruction_coverage':coverage,'live_input_lifecycle':live,
 'unrecovered_lifecycle':'Original Input startup, both device tasks and cleanup now run through the shared object factory and component updater. Twelve remaining Input commands and their complete descriptor registration, skater scene assembly, camera, rendered frames, production audio/file services and a playable original training level remain unfinished. Prior training traces remain unchanged.',
 'coverage_limit':'700/707 instructions; seven allocation-failure instructions remain unexercised, no exclusions. Successful task allocation is required because original bind dereferences a failed allocation. Generic test owner and initialized device services are not full skater startup. DirectInput COM fixture observes arguments only; it is not production browser haptics. Previous limits still apply.',
 'artifact_hashes':dict(sorted(artifacts.items())),'harness_hashes':dict(sorted(harnesses.items())),
 'browser_dom_fingerprint':fp,'playable':False,'scope':fixture['scope']}
assert checkpoint['main_wasm_sha256']==prior['main_wasm_sha256']
target.write_text(json.dumps(checkpoint,indent=2)+'\n');print('PINNED',len(artifacts),'artifacts',len(harnesses),'harnesses',sha(target))
