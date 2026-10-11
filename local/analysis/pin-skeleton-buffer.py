"""Pin the actually observed Chromium checkpoint and its unchanged predecessors."""
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof_path=folder/'skeleton-buffer-browser.json';pin_path=folder/'skeleton-buffer-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(folder/'training-startup-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
    for name,digest in prior[group].items():assert sha(root/name)==digest,(group,name)
build=read(folder/'skeleton-buffer-draft.build.json')
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/name)==digest,name
module=folder/'skeleton-buffer-draft.wasm'
assert sha(module)==build['sha256']=='039eac04857d318f72c96960b8ebf974204276bdad24d7e15ddc363b8db2ea57'
suites={n.replace('-','_'):read(folder/('skeleton-checkpoint-'+n+'-result.json')) for n in ['skeleton-buffer','script-change','training-startup']}
assert all(r['result']=='pass' for r in suites.values())
assert (suites['skeleton_buffer']['cases'],suites['skeleton_buffer']['calls'],suites['skeleton_buffer']['nan_fields_classification_only'])==(463,809,366)
assert suites['skeleton_buffer']==read(folder/'skeleton-buffer-result.json')
assert suites['script_change']==read(folder/'script-change-result.json')
assert suites['training_startup']==read(folder/'training-startup-result.json')
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,ensure_ascii=False,sort_keys=True,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='a317e756f469e971'
assert int(sys.argv[2])==len(canonical)==3113 and int(sys.argv[3])==len(candidate)==5
original=read(folder/'skeleton-buffer-original.json');fixture=read(folder/'skeleton-buffer-fixtures.json')
assert len(original['assets'])==58
for a in original['assets']:assert sha(root/a['path'])==a['sha256']
# Real assets have no numerical exceptions. Typed NaN allowances occur only
# in the five deliberately aliased object/file cases, never raw input fields.
for label,case in zip(fixture['case_labels'],fixture['cases']):
    if not label.startswith('in-place object/file '):assert all(not s.get('float_fields') for s in case['steps'])
scope='Four additional routines recover complete internal skeleton-buffer parsing, object lifetime and quaternion/translation matrix conversion. All58 real loose skeletons match exact arithmetic bits; computed NaNs in deliberately aliased object/file cases use classification. The new build contains maintained main plus Change and these4 routines, not the prior17 physics experiments. Actual training startup still stops before LoadSkeleton; asset/file integration remains. Not playable and not promoted to the main recovery count.'
proof={**candidate,'recorded_at':sys.argv[4],
 'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all three suite summaries and the entire DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
names=['skeleton-buffer-draft.c','skeleton-buffer-draft.wasm','skeleton-buffer-draft.build.json','build-skeleton-buffer-draft.py',
 'probe-skeleton-buffer.py','skeleton-buffer-instructions.txt','skeleton-buffer-fixtures.json','skeleton-buffer-memory.bin',
 'skeleton-buffer-original.json','skeleton-buffer-result.json','verify-skeleton-buffer.mjs','verify-skeleton-checkpoint.mjs',
 'skeleton-checkpoint-skeleton-buffer-result.json','skeleton-checkpoint-script-change-result.json','skeleton-checkpoint-training-startup-result.json',
 'skeleton-buffer-browser.html','skeleton-buffer-worker.mjs','serve-skeleton-buffer.py','skeleton-buffer-browser.json','pin-skeleton-buffer.py',
 'skeleton-file-symbols.tsv','skeleton-file-next-instructions.txt']
artifacts=set(prior['artifact_hashes'])|{'local/analysis/training-startup-checkpoint.json'}
artifacts.update('local/analysis/'+n for n in names)
artifacts.update(a['path'] for a in original['assets'])
for directory in ['skeleton-loading-ghidra','skeleton-file-ghidra']:
    artifacts.update(str(p.relative_to(root)) for p in (folder/directory).rglob('*') if p.is_file())
memory_fixture=folder/fixture['memory_fixture']
if not memory_fixture.exists():memory_fixture=root/'local/validation/collision'/fixture['memory_fixture']
artifacts.add(str(memory_fixture.relative_to(root)))
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted',
 'new_functions':4,'original_addresses':['0x463aa0','0x4a2c20','0x4a3950','0x4a39c0'],
 'unpromoted_functions_across_separate_experiments':22,'specimen_sha256':original['specimen_sha256'],
 'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':3,'new_cases':463,'new_calls':809,'real_skeleton_files':58,
 'instruction_coverage':original['instruction_coverage'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n')
assert sha(root/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),
 'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
