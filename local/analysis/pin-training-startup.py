"""Preserve the observed Chromium report and all inputs to the partial trace."""
import hashlib,json,sys
from pathlib import Path
root=Path.cwd();folder=root/'local/analysis'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof_path=folder/'training-startup-browser.json';pin_path=folder/'training-startup-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(folder/'physics-command-values-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
    for name,digest in prior[group].items():assert sha(root/name)==digest,(group,name)
build=read(folder/'script-change-draft.build.json')
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(root/name)==digest,name
module=folder/'script-change-draft.wasm'
assert sha(module)==build['sha256']=='38531f6aba6af92d732014708d1dba2b09bf410f317d0af96990cab623de048f'
suites={n.replace('-','_'):read(folder/(n+'-result.json')) for n in ['script-change','training-startup']}
assert all(r['result']=='pass' and not r['nan_fields_classification_only'] for r in suites.values())
assert (suites['script_change']['cases'],suites['script_change']['calls'])==(616,1229)
assert (suites['training_startup']['completed_setup_calls'],suites['training_startup']['interrupted_execute_calls'])==(4,1)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,ensure_ascii=False,sort_keys=True,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='7be51508d3d90e72'
assert int(sys.argv[2])==len(canonical)==2040 and int(sys.argv[3])==len(candidate)==5
original=read(folder/'training-startup-original.json');change=read(folder/'script-change-original.json')
assert (original['tod_value_before'],original['tod_value_after'])==(0,1)
assert original['native_entries']=={'0x449d00':1,'0x445640':1}
assert original['next_missing_handler']['address']=='0x445640'
assert change['instruction_coverage']['0x449d00']['covered']==196
scope='One additional native command recovered, with 616 direct cases and a partial execution of unchanged original training QB after two actual file loads. Startup is deliberately interrupted before LoadSkeleton; no handler success, full startup or playable level is claimed. Main159-suite checkpoint and prior17 experimental physics routines remain unchanged; the Change module contains main plus Change, not those17 experiments.'
proof={**candidate,'recorded_at':sys.argv[4],
       'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; both suite summaries and full DOM fingerprint inspected',
       'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},
       'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/physics-command-values-checkpoint.json'}
names=['script-change-draft.c','script-change-draft.wasm','script-change-draft.build.json','build-script-change-draft.py',
       'script-change-instructions.txt','probe-script-change.py','script-change-fixtures.json','script-change-memory.bin','script-change-original.json','script-change-result.json','verify-script-change.mjs',
       'probe-training-startup.py','training-startup-fixtures.json','training-startup-memory.bin','training-startup-original.json','training-startup-result.json',
       'training-startup-checks.mjs','training-startup-boundary.c','training-startup-boundary.wasm','verify-training-startup.mjs',
       'training-startup-browser.html','training-startup-worker.mjs','serve-training-startup.py','training-startup-browser.json','pin-training-startup.py',
       'training-skeleton-next-instructions.txt','training-skeleton-next-discovery.json']
artifacts.update('local/analysis/'+n for n in names)
for n in ['script-change','training-startup']:
    fixture=read(folder/(n+'-fixtures.json'))
    for filename in [fixture['memory_fixture']]+[row['module'] for row in fixture.get('native_callbacks',[])]:
        p=folder/filename
        if not p.exists():p=root/'local/validation/collision'/filename
        artifacts.add(str(p.relative_to(root)))
artifacts.add('local/game-files/Game/Data/scripts/engine/tod_manager.qb')
artifacts.add('local/game-files/Game/Data/skeletons/CS_Cardboard.ske.xbx')
for p in (folder/'training-startup-ghidra').rglob('*'):
    if p.is_file():artifacts.add(str(p.relative_to(root)))
pin={'result':'original, Node and Chromium partial-startup comparisons pass; not promoted',
     'new_functions':1,'new_original_address':'0x449d00','unpromoted_functions_across_separate_experiments':18,
     'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,
     'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':2,'direct_cases':616,'direct_calls':1229,
     'startup_cases':1,'completed_startup_setup_calls':4,'interrupted_startup_execute_calls':1,
     'instruction_coverage':change['instruction_coverage'],'next_missing_handler':original['next_missing_handler'],
     'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(root/n) for n in sorted(artifacts)},
     'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
     'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'source_files':len(pin['source_hashes']),
                  'direct_cases':616,'direct_calls':1229,'startup_reached':'LoadSkeleton; deliberately interrupted',
                  'checkpoint_sha256':sha(pin_path)}))
