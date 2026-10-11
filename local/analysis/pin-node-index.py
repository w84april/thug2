"""Freeze the observed node-index checkpoint once; preserve all earlier identities."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'node-index-browser.json';pin_path=p/'node-index-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior_path=p/'scene-kill-checkpoint.json'
assert sha(prior_path)=='7123ed980540ab8719b018364590c49e79d403cf9f4d8499357b8528b731de52'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'node-index-draft.build.json');module=p/'node-index-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='9ff1843df45d8be3f34709eaba346e9ce825378c9512e664a01ab58a8d91b491'
assert module.stat().st_size==508870
names=['node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('node-index-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('scene-kill-checkpoint-'+n+'-result.json'))
assert (suites['node_index']['cases'],suites['node_index']['calls'])==(93,127)
assert (suites['training_node_index']['cases'],suites['training_node_index']['calls'])==(1,6)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='0ccfa7987e5a75b9'
assert int(sys.argv[2])==len(canonical)==20063 and int(sys.argv[3])==len(candidate)==5
original=read(p/'node-index-original.json');coverage=original['instruction_coverage']
assert len(coverage)==12 and sum(c['total'] for c in coverage.values())==547
assert sum(c['covered'] for c in coverage.values())==541
excluded={n for c in coverage.values() for n in c['excluded']}
assert excluded=={'0x45c28d','0x45c5f2','0x45c623','0x45c6cd','0x45c762','0x45c931'}
assert all(set(c['missing'])==set(c['excluded']) for c in coverage.values())
training=read(p/'training-node-index-original.json')
assert training['nodes']==training['occupied_name_slots']==1917
assert len(training['prefix_names'])==5 and training['freeskate_node_index']==1436
assert training['specimen_sha256']==original['specimen_sha256']
scope='Twelve additional original routines recover name-table indexing, readable local names, full prefix building and link conversion. Eighteen actual Chromium suites pass. The unchanged training QB file loads and all1917 nodes are indexed, with links converted, five career-prefix targets in original order and freeskate wall1436 resolved. Single-array registration metadata is caller-bound test state; full45d520 registration, coordinate conversion and optional link-group/reference postprocessing are not implemented here. The previous completed TR_startup and interrupted TR_Setup comparisons remain unchanged. No playable level; main and separate17 physics build unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all eighteen suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=['node-index-draft.c','node-index-draft.wasm','node-index-draft.build.json','build-node-index-draft.py',
 'probe-node-index.py','node-index-fixtures.json','node-index-memory.bin','node-index-original.json',
 'probe-training-node-index.py','training-node-index-fixtures.json','training-node-index-memory.bin','training-node-index-original.json',
 'node-index-function-instructions.txt','verify-node-index-checkpoint.mjs','node-index-browser.html','node-index-worker.mjs','serve-node-index.py',
 'node-index-browser.json','pin-node-index.py','audit-node-index.py','node-registration-ghidra.log','node-iteration-ghidra.log']
files+=['node-index-checkpoint-'+n+'-result.json' for n in names]
for directory in ['node-registration-ghidra','node-iteration-ghidra']:
 files += [str(n.relative_to(p)) for n in sorted((p/directory).rglob('*')) if n.is_file()]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-kill-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':12,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':81,'unpromoted_functions_across_separate_experiments':98,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':18,'new_cases':94,'new_calls_including_existing_loader_and_lookups':133,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
