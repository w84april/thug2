"""Freeze the observed shared-object-builder checkpoint and prior evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'composite-construction-browser.json';pin_path=p/'composite-construction-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior_path=p/'node-registration-checkpoint.json'
assert sha(prior_path)=='a123aa9014837f5ef8931adbe3b904ec847a702960d485edd21707df74357a6f'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'composite-construction-draft.build.json');module=p/'composite-construction-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='e60d732333364553bfa4a0de26590a06ee8acdba9a04549cd0b28cf9a2e866b5'
assert module.stat().st_size==517315
names=['composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('composite-construction-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('node-registration-checkpoint-'+n+'-result.json'))
assert (suites['composite_math']['cases'],suites['composite_math']['calls'],suites['composite_math']['nan_fields_classification_only'])==(491,491,622)
assert (suites['composite_construction']['cases'],suites['composite_construction']['calls'],suites['composite_construction']['nan_fields_classification_only'])==(96,283,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='388a639ae448c73b'
assert int(sys.argv[2])==len(canonical)==25323 and int(sys.argv[3])==len(candidate)==5
originals=[read(p/(n+'-original.json')) for n in names[:2]]
coverage={k:v for report in originals for k,v in report['instruction_coverage'].items()}
assert len(coverage)==17 and sum(c['total'] for c in coverage.values())==638
assert sum(c['covered'] for c in coverage.values())==637
assert {n for c in coverage.values() for n in c['excluded']}=={'0x45ee9b'}
assert all(set(c['missing'])==set(c['excluded']) for c in coverage.values())
assert len({o['specimen_sha256'] for o in originals})==1
inventory=read(p/'gameobject-component-inventory.json')
assert inventory['descriptor_array']['count']==4
assert [c['type'] for c in inventory['descriptor_array']['components']]==['0xce0ca665','0xa015e17','0x1d5b1ae6','0x7713c7b']
scope='Seventeen additional original routines recover node quaternion orientation and shared composite construction/lifetime. Twenty-two actual Chromium suites pass. Real base object and physics-component construction, registry bookkeeping, parameter merging, finalization and deferred deletion execute. Explicit test witnesses cover live callback mutations without supplying gameplay implementations. Nine computed matrix words permit NaN classification only for arithmetic NaNs; all other new comparisons are exact. Successful allocation and initialized services are test contracts. Original-only script inspection identifies the four actual prop descriptor types and their factories. Prop-specific components/scripts, full scene creation/rendering and playable training remain; TR_Setup still stops at its previous boundary. Main and separate physics build unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all22 suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['composite-construction-draft.c','composite-construction-draft.wasm','composite-construction-draft.build.json','build-composite-construction-draft.py',
 'composite-construction-fixture-setup.py','probe-composite-math.py','composite-math-fixtures.json','composite-math-memory.bin','composite-math-original.json',
 'probe-composite-construction.py','composite-construction-fixtures.json','composite-construction-memory.bin','composite-construction-original.json',
 'composite-construction-callback.c','composite-construction-callback.wasm','composite-construction-callback.build.json','composite-construction-callback-setup.py',
 'composite-construction-function-instructions.txt','verify-composite-construction-checkpoint.mjs','composite-construction-browser.html','composite-construction-worker.mjs','serve-composite-construction.py',
 'composite-construction-browser.json','pin-composite-construction.py','audit-composite-construction.py',
 'trace-gameobject-components.py','gameobject-component-inventory.json','map-prop-component-dependencies.py','prop-component-dependencies.json','prop-component-vtables.json','prop-component-focus.tsv']
files+=['composite-construction-checkpoint-'+n+'-result.json' for n in names]
for directory in ['composite-construction-ghidra','composite-lifecycle-ghidra','prop-components-ghidra','prop-component-methods-ghidra']:
 files += [directory+'.log']+[str(n.relative_to(p)) for n in sorted((p/directory).rglob('*')) if n.is_file()]
for n in files:
 if n!='composite-construction-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/node-registration-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':17,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':110,'unpromoted_functions_across_separate_experiments':127,
 'specimen_sha256':originals[0]['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':22,'new_cases':587,'new_calls_including_existing_dependencies':774,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
