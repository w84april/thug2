"""Freeze the original/Node/observed-Chromium checkpoint once only."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'scene-state-browser.json';pin_path=p/'scene-state-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(p/'training-mode-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'scene-state-draft.build.json');module=p/'scene-state-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='11f8a1abd992288cd10d979f7f3b5a32c286e4f3c0c2f5a40fcdcee5142c5e08'
names=['scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('scene-state-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:3]:assert suites[n.replace('-','_')]==read(p/(n+'-result.json'))
assert [(suites[n]['cases'],suites[n]['calls']) for n in ['scene_state','scene_disposal','scene_visitor']]==[(796,1321),(217,581),(131,203)]
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='817720aea35c1c00'
assert int(sys.argv[2])==len(canonical)==12781 and int(sys.argv[3])==len(candidate)==5
originals=[read(p/(n+'-original.json')) for n in names[:3]]
coverage={k:v for original in originals for k,v in original['instruction_coverage'].items()}
assert len(coverage)==9 and sum(c['total'] for c in coverage.values())==350 and all(not c['missing'] for c in coverage.values())
scope='Nine additional scene-state dependencies: scene-list first, network-mode predicate, rail/emitter enabling, geometry collision flags and renderer dispatch, table clearing, both light-list removal paths and reentrant object traversal. Full original comparisons and twelve actual Chromium suites pass. Renderer and visitor callbacks are explicit test witnesses, not gameplay substitutions. The original TR_Setup trace still stops before Kill; proximity state, auxiliary geometry state, concrete object destruction and remaining scene dispatch remain. No production renderer, completed scene boot or playable level. Main and separate17 physics experiment unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all twelve suite summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=['scene-state-draft.c','scene-state-draft.wasm','scene-state-draft.build.json','build-scene-state-draft.py',
 'build-scene-witnesses.py','scene-state-witnesses.build.json','verify-scene-state.mjs','verify-scene-state-checkpoint.mjs',
 'scene-state-browser.html','scene-state-worker.mjs','serve-scene-state.py','scene-state-browser.json','pin-scene-state.py','audit-scene-state.py',
 'scene-state-callback.c','scene-state-callback.wasm','scene-disposal-memory.c','scene-disposal-memory.wasm','scene-visitor-callback.c','scene-visitor-callback.wasm',
 'scene-state-instructions.txt','scene-lifetime-instructions.txt','scene-lifetime-symbols.tsv']
for n in names[:3]:files+=['probe-'+n+'.py',n+'-fixtures.json',n+'-memory.bin',n+'-original.json']
files+=['scene-state-checkpoint-'+n+'-result.json' for n in names]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/training-mode-checkpoint.json'}|{'local/analysis/'+n for n in files}
for folder in ['scene-state-ghidra','scene-lifetime-ghidra']:
 artifacts.update(str(f.relative_to(r)) for f in (p/folder).rglob('*') if f.is_file())
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':9,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':53,'unpromoted_functions_across_separate_experiments':70,
 'specimen_sha256':originals[0]['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':12,'new_direct_cases':1144,'new_direct_calls':2105,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
