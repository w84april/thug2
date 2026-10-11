"""Freeze the observed complete-registration checkpoint; preserve previous hashes."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'node-registration-browser.json';pin_path=p/'node-registration-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior_path=p/'node-index-checkpoint.json'
assert sha(prior_path)=='303a5cf376f2a34baacc14472338d58d906d699a9e6a44e54bb8ff17e19d588b'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'node-registration-draft.build.json');module=p/'node-registration-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='be14e6de7c53ca753e0c83f15b9c4903cc3e77e2e51ea591ca8437bbe0f4df22'
assert module.stat().st_size==512204
names=['node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('node-registration-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('node-index-checkpoint-'+n+'-result.json'))
assert (suites['node_registration']['cases'],suites['node_registration']['calls'])==(151,391)
assert suites['node_registration']['signaling_nan_words_quieted_per_x87']==28
assert (suites['training_node_registration']['cases'],suites['training_node_registration']['calls'])==(2,12)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='2a1a1e55c614105c'
assert int(sys.argv[2])==len(canonical)==22975 and int(sys.argv[3])==len(candidate)==5
original=read(p/'node-registration-original.json');coverage=original['instruction_coverage']
assert len(coverage)==12 and sum(c['total'] for c in coverage.values())==408
assert sum(c['covered'] for c in coverage.values())==404
assert {n for c in coverage.values() for n in c['excluded']}=={'0x4694f2','0x46952d','0x46952f','0x46979d'}
assert all(set(c['missing'])==set(c['excluded']) for c in coverage.values())
training=read(p/'training-node-registration-original.json')
assert training['specimen_sha256']==original['specimen_sha256']
for case in training['registrations']:
 assert case['nodes']==case['occupied_name_slots']==1917
 assert len(case['prefix_names'])==5 and case['freeskate_node_index']==1436
 assert case['duplicate_result']==0 and case['group_count']==(10 if case['postprocess'] else 0xffffffff)
inventory=read(p/'training-scene-node-inventory.json')
assert inventory['node_count']==1917 and inventory['link_groups']==10
scope='Twelve additional original entry points recover complete node-array registration, iteration, link access and link-group/reference processing. Twenty actual Chromium suites pass. The unchanged training QB registers all1917 nodes with real name/prefix indexes, coordinate conversion, link rewriting, optional10-group assignment and duplicate rejection. No caller-bound registration metadata is substituted. Initialized runtime, successful heap services and reference-list manager remain explicit test starting state. Signaling-NaN synthetic Y/Z fields require exact Intel quiet bits, with raw emulator discrepancies retained. TR_Setup still stops at its previous boundary; scene creation/rendering and playable training remain. Main and separate17 physics build unchanged. Original-only creation-flag inventory and static creation/parse analysis identify next dependencies.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all twenty suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['node-registration-draft.c','node-registration-draft.wasm','node-registration-draft.build.json','build-node-registration-draft.py',
 'probe-node-registration.py','node-registration-fixtures.json','node-registration-memory.bin','node-registration-original.json','node-registration-x87-differences.json',
 'probe-training-node-registration.py','training-node-registration-fixtures.json','training-node-registration-memory.bin','training-node-registration-original.json',
 'node-registration-function-instructions.txt','verify-node-registration-checkpoint.mjs','node-registration-browser.html','node-registration-worker.mjs','serve-node-registration.py',
 'node-registration-browser.json','pin-node-registration.py','audit-node-registration.py',
 'node-creation-ghidra.log','node-parse-ghidra.log','trace-training-scene-nodes.py','training-scene-node-inventory.json']
files+=['node-registration-checkpoint-'+n+'-result.json' for n in names]
for directory in ['node-creation-ghidra','node-parse-ghidra']:
 files += [str(n.relative_to(p)) for n in sorted((p/directory).rglob('*')) if n.is_file()]
for n in files:
 if n!='node-registration-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/node-index-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':12,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':93,'unpromoted_functions_across_separate_experiments':110,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':20,'new_cases':153,'new_calls_including_existing_loader_and_lookups':403,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
