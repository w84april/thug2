"""Pin a completed original/Node/observed Chromium comparison, once only."""
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();p=root/'local/analysis'
read=lambda x:json.loads(x.read_text())
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'asset-factory-browser.json';pin_path=p/'asset-factory-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(p/'skeleton-asset-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(root/name)==digest,(group,name)
build=read(p/'asset-factory-draft.build.json');module=p/'asset-factory-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/name)==digest,name
assert sha(module)==build['sha256']=='2dc66f0be466a1c79524fe94ae4d74032944240a3e64b421412773f20ef157c4'
names=['asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('asset-factory-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 assert suites[n.replace('-','_')]==read(p/(n+'-result.json'))
assert (suites['asset_factory']['cases'],suites['asset_factory']['calls'],suites['asset_factory']['nan_fields_classification_only'])==(738,790,0)
assert (suites['training_load']['calls'],suites['training_load']['execute_result'],suites['training_load']['final_instruction'],suites['training_load']['ready_skeleton_bones'])==(5,0,0,34)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='b7a05bf9bd0aa4a5'
assert int(sys.argv[2])==len(canonical)==6493 and int(sys.argv[3])==len(candidate)==5
original=read(p/'asset-factory-original.json');startup=read(p/'training-load-original.json')
assert len(original['instruction_coverage'])==22
assert sum(c['covered'] for c in original['instruction_coverage'].values())==597
assert sum(c['total'] for c in original['instruction_coverage'].values())==600
assert startup['native_entries']=={'0x449d00':1,'0x445640':1}
assert startup['asset']['state']==4 and startup['asset']['bones']==34
assert startup['asset']['file_closed'] and startup['asset']['read_buffer_released']
for a in startup['sources']:
 if 'path' in a:assert sha(root/a['path'])==a['sha256']
 else:assert any(b['member']==a['member'] and b['sha256']==a['sha256'] for b in read(root/'local/validation/script-tokens.json')['assets'])
scope='Twenty-two additional original asset-factory and native routines, plus complete execution of unchanged TR_startup from initialized services. Factory comparison instruments class virtuals only as test witnesses; the actual startup invokes recovered skeleton loading/parsing with original34-bone asset bytes and explicit resident-file/heap port services. It changes the time-of-day value, registers the ready skeleton, closes/releases temporary loading resources and returns with a null instruction pointer. This is not cold engine boot, complete level setup, production file/archive access or playable training. Main recovery and the separate17 physics experiment remain unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all five suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
new_names=['asset-factory-draft.c','asset-factory-draft.wasm','asset-factory-draft.build.json','build-asset-factory-draft.py',
 'probe-asset-factory.py','asset-factory-fixtures.json','asset-factory-memory.bin','asset-factory-original.json','asset-factory-result.json',
 'asset-factory-callbacks.c','asset-factory-callbacks.wasm','verify-asset-factory.mjs','verify-asset-factory-checkpoint.mjs',
 'asset-factory-browser.html','asset-factory-worker.mjs','serve-asset-factory.py','asset-factory-browser.json','pin-asset-factory.py',
 'probe-training-load.py','training-load-fixtures.json','training-load-memory.bin','training-load-original.json','training-load-result.json',
 'training-load-io.c','training-load-io.wasm','verify-training-load.mjs','inspect-training-entrypoints.mjs','training-entrypoints-discovery.json']
new_names += ['asset-factory-checkpoint-'+n+'-result.json' for n in names]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/skeleton-asset-checkpoint.json'}|{'local/analysis/'+n for n in new_names}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':22,'original_addresses':list(original['instruction_coverage']),
 'unpromoted_functions_in_this_module':40,'unpromoted_functions_across_separate_experiments':57,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,
 'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':5,'new_cases':738,'new_calls':790,
 'completed_training_startup_cases':1,'completed_training_startup_calls':5,'ready_training_skeleton_bones':34,
 'instruction_coverage':original['instruction_coverage'],'source_hashes':build['source_hashes'],
 'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],
 'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n')
assert sha(root/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
