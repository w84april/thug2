"""Pin the observed training mode and scene lookup comparisons, once only."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'training-mode-browser.json';pin_path=p/'training-mode-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(p/'asset-factory-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'training-mode-draft.build.json');module=p/'training-mode-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='ec8fffbf9b619a49f4bfb3968f47ad53b2bf190d816c48d341c73f3fd7db1c3b'
names=['training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('training-mode-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 assert suites[n.replace('-','_')]==read(p/(n+'-result.json'))
assert [(suites[n]['cases'],suites[n]['calls']) for n in ['training_mode','node_prefix','scene_name']]==[(545,545),(106,212),(334,334)]
assert (suites['training_setup']['completed_setup_calls'],suites['training_setup']['interrupted_execute_calls'])==(10,2)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='ba1cc970be591b70'
assert int(sys.argv[2])==len(canonical)==9765 and int(sys.argv[3])==len(candidate)==5
originals=[read(p/(n+'-original.json')) for n in ['training-mode','node-prefix','scene-name']]
coverage={k:v for original in originals for k,v in original['instruction_coverage'].items()}
assert len(coverage)==4 and sum(c['total'] for c in coverage.values())==174 and all(not c['missing'] for c in coverage.values())
startup=read(p/'training-setup-original.json')
assert [o['game_mode_result'] for o in startup['observations']]==[1,0]
assert all(o['native_entries']=={'0x5a11d0':1,'0x5a5030':1} for o in startup['observations'])
for a in startup['sources']:
 if 'path' in a:assert sha(r/a['path'])==a['sha256']
 else:assert any(b['member']==a['member'] and b['sha256']==a['sha256'] for b in read(r/'local/validation/script-tokens.json')['assets'])
scope='Four additional routines recover game-mode selection and two scene-name/prefix lookup dependencies. Actual unchanged TR_Setup reaches Kill after different career/free-skate branches with mode settings resolved from original gamemode.qb. Both executions intentionally stop before Kill; no scene mutation is simulated. Prefix indexes are fixture-populated, not produced by the unrecovered node loader. Prior completed TR_startup/skeleton loading is retained. This initialized-runtime experimental build is not cold boot or playable training. Main engine and separate17 physics experiment remain unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all nine suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=['training-mode-draft.c','training-mode-draft.wasm','training-mode-draft.build.json','build-training-mode-draft.py',
 'verify-training-mode-checkpoint.mjs','training-mode-browser.html','training-mode-worker.mjs','serve-training-mode.py','training-mode-browser.json','pin-training-mode.py',
 'training-setup-boundary.c','training-setup-boundary.wasm','training-setup-checks.mjs','trace-training-setup.py','training-setup-next-trace.json',
 'training-setup-next-instructions.txt','scene-kill-next-instructions.txt']
for n in ['training-mode','node-prefix','scene-name','training-setup']:
 files += ['probe-'+n+'.py','verify-'+n+'.mjs',n+'-fixtures.json',n+'-memory.bin',n+'-original.json',n+'-result.json']
files += ['training-mode-checkpoint-'+n+'-result.json' for n in names]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/asset-factory-checkpoint.json'}|{'local/analysis/'+n for n in files}
for folder in ['training-setup-ghidra','node-operation-ghidra','scene-kill-ghidra']:
 artifacts.update(str(f.relative_to(r)) for f in (p/folder).rglob('*') if f.is_file())
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':4,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':44,'unpromoted_functions_across_separate_experiments':61,
 'specimen_sha256':originals[0]['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':9,'new_direct_cases':985,'new_direct_calls':1091,'partial_setup_cases':2,'completed_setup_calls':10,'interrupted_execute_calls':2,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
