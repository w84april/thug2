"""Pin the observed original, Node and Chromium Model-construction checkpoint."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
pin_path=p/'model-component-checkpoint.json';proof_path=p/'model-component-browser.json'
assert not pin_path.exists() and not proof_path.exists()
prior_path=p/'prop-command-checkpoint.json'
assert sha(prior_path)=='81ccfbe0ac3a03e80a7e95273e7081fa4073031f91f2c1b94d852efd3202777c'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'model-component-draft.build.json');module=p/'model-component-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='777cbcfa6d7a027a789b621ba54c21806469572c755bb740193f9afa70b129da'
assert module.stat().st_size==540719
names=['model-component','training-model-component','prop-command','training-prop-script','prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('model-component-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('prop-command-checkpoint-'+n+'-result.json'))
assert (suites['model_component']['cases'],suites['model_component']['calls'],suites['model_component']['nan_fields_classification_only'])==(51,66,0)
assert (suites['training_model_component']['cases'],suites['training_model_component']['calls'],suites['training_model_component']['nan_fields_classification_only'])==(2,22,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'model-component-original.json');coverage=original['instruction_coverage']
assert len(coverage)==7 and sum(c['covered'] for c in coverage.values())==169 and sum(c['total'] for c in coverage.values())==181
for c in coverage.values():assert set(c['missing'])==set(c['excluded'])
training=read(p/'training-model-component-original.json');assert training['cases']==2 and training['calls']==22
assert training['nodes'][0]['execute_result']==0 and training['nodes'][0]['final_instruction']=='0x0'
node=training['nodes'][1];assert node['node_index']==1289 and node['first_missing_routine']=='0x4214f0'
for a in ['0x421490','0x420bf0','0x48bfa0','0x4b29c0','0x4bad90','0x494c40']:assert node['native_entries'][a]==1
assert node['model_state']['owner_components']==['0xce0ca665','0xa015e17','0x1d5b1ae6','0x7713c7b','0x286a8d26']
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
scope='Seven additional original routines recover complete Model component and nested renderer construction, including the circular-list sentinel and actual shared true virtual. All29 Chromium suites pass; all27 prior summaries are unchanged. New53 cases88 calls compare full arenas/globals/allocation effects and original preserved registers without NaN allowances. Instruction coverage169/181 has12 explicit bootstrap/successful-allocation exclusions. The unchanged training QB files register all1917nodes in each integration case. Node204 script completes; node1289 SKATE letter S executes actual model/component/renderer factories, attaches Model as its fifth component and reaches initializer4214f0. A test-only method breakpoint records arguments and traps before initialization, providing no result or asset-loading behavior. Both live host service scopes at that breakpoint are checked, including stack bounds and arguments; normal returns restore their caller scopes. Model initialization/loading, destruction, update/draw and complete468cb0 assembly remain unavailable. No renderer output or playable level is claimed. Main and separate physics builds remain unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all29 suite summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['model-component-draft.c','model-component-draft.wasm','model-component-draft.build.json','build-model-component-draft.py',
 'probe-model-component.py','model-component-fixtures.json','model-component-memory.bin','model-component-original.json','model-component-probe.log',
 'model-component-focus.tsv','model-component-initial-discovery.txt','model-component-instructions.txt','model-component-methods.json','model-component-letter-assets.json',
 'probe-training-model-component.py','training-model-component-fixtures.json','training-model-component-memory.bin','training-model-component-original.json','training-model-component-probe.log',
 'training-model-component-boundary.c','training-model-component-boundary.wasm','training-model-component-boundary.build.json','training-model-component-checks.mjs',
 'verify-model-component-checkpoint.mjs','model-component-full-node.log','model-component-browser.html','model-component-worker.mjs','serve-model-component.py','model-component-browser.json','pin-model-component.py','audit-model-component.py']
files+=['model-component-checkpoint-'+n+'-result.json' for n in names]
files+=['model-component-ghidra.log']+[str(f.relative_to(p)) for f in sorted((p/'model-component-ghidra').rglob('*')) if f.is_file()]
for n in files:
 if n!='model-component-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/prop-command-checkpoint.json','local/analysis/prop-command-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':7,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':195,'unpromoted_functions_across_separate_experiments':212,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':29,'new_cases':53,'new_calls_including_existing_dependencies':88,'actual_training_model_component_cases':2,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
