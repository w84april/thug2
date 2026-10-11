"""Preserve the observed browser run without changing earlier checkpoints."""
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof_path=folder/'skeleton-asset-browser.json';pin_path=folder/'skeleton-asset-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(folder/'skeleton-buffer-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
    for name,digest in prior[group].items():assert sha(root/name)==digest,(group,name)
build=read(folder/'skeleton-asset-draft.build.json')
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/name)==digest,name
module=folder/'skeleton-asset-draft.wasm'
assert sha(module)==build['sha256']=='58b1c9dd932a211f626d6f9fce9827bfd283eeddd48c3699b974e3bd63494201'
suite_names=['skeleton-asset','skeleton-buffer','script-change','training-startup']
suites={n.replace('-','_'):read(folder/('skeleton-asset-checkpoint-'+n+'-result.json')) for n in suite_names}
assert all(r['result']=='pass' for r in suites.values())
assert (suites['skeleton_asset']['cases'],suites['skeleton_asset']['calls'],suites['skeleton_asset']['nan_fields_classification_only'])==(310,1220,0)
for name in suite_names:assert suites[name.replace('-','_')]==read(folder/(name+'-result.json'))
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,ensure_ascii=False,sort_keys=True,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='46378022fd0c02e6'
assert int(sys.argv[2])==len(canonical)==4658 and int(sys.argv[3])==len(candidate)==5
original=read(folder/'skeleton-asset-original.json');fixture=read(folder/'skeleton-asset-fixtures.json')
assert len(original['assets'])==58 and len(original['instruction_coverage'])==13
for a in original['assets']:assert sha(root/a['path'])==a['sha256']
assert original['io_calls']=={'0x5b68a0':232,'0x5b6c60':123,'0x5b63a0':116,'0x5b6740':116}
scope='Thirteen additional asset routines match original instructions with explicit memory and resident-file port interfaces. All58 skeleton files exercise immediate and deferred loading, parsing and cleanup. The file provider is comparison-only; original archive/Windows I/O and production browser file access are not claimed. New build contains main plus Change,4 skeleton and13 asset routines; separate17 physics routines remain separate. The existing real training trace still stops before LoadSkeleton; not playable or promoted.'
proof={**candidate,'recorded_at':sys.argv[4],
 'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all four suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
names=['skeleton-asset-draft.c','skeleton-asset-draft.wasm','skeleton-asset-draft.build.json','build-skeleton-asset-draft.py',
 'probe-skeleton-asset.py','skeleton-asset-instructions.txt','skeleton-asset-fixtures.json','skeleton-asset-memory.bin',
 'skeleton-asset-original.json','skeleton-asset-result.json','skeleton-asset-io.c','skeleton-asset-io.wasm',
 'verify-skeleton-asset.mjs','verify-skeleton-asset-checkpoint.mjs','skeleton-asset-browser.html','skeleton-asset-worker.mjs',
 'serve-skeleton-asset.py','skeleton-asset-browser.json','pin-skeleton-asset.py','asset-factory-next-instructions.txt']
names += ['skeleton-asset-checkpoint-'+n+'-result.json' for n in suite_names]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/skeleton-buffer-checkpoint.json'}
artifacts.update('local/analysis/'+n for n in names)
artifacts.update(str(p.relative_to(root)) for p in (folder/'asset-factory-ghidra').rglob('*') if p.is_file())
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'new_functions':13,'original_addresses':list(original['instruction_coverage']),
 'unpromoted_functions_across_separate_experiments':35,'specimen_sha256':original['specimen_sha256'],
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':4,'new_cases':310,'new_calls':1220,'real_skeleton_files':58,
 'instruction_coverage':original['instruction_coverage'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n')
assert sha(root/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),
 'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
