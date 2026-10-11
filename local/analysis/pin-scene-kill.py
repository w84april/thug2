"""Freeze the observed Kill checkpoint once only; retain every earlier identity."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'scene-kill-browser.json';pin_path=p/'scene-kill-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(p/'scene-lifetime-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'scene-kill-draft.build.json');module=p/'scene-kill-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='c537ed35f66d87ab4e62ac27b4a578d3e25743d9cc2c6a93d7ca382c7ffc9a53'
names=['scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('scene-kill-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n!='scene-kill':assert suites[n.replace('-','_')]==read(p/('scene-lifetime-checkpoint-'+n+'-result.json'))
assert (suites['scene_kill']['cases'],suites['scene_kill']['calls'])==(148,279)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'
assert int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'scene-kill-original.json');coverage=original['instruction_coverage']
assert len(coverage)==5 and sum(c['total'] for c in coverage.values())==205
assert all(c['covered']==c['total'] and not c['missing'] for c in coverage.values())
discovery=read(p/'training-node-index-discovery.json')
assert discovery['node_count']==discovery['occupied_name_slots']==1917
assert len(discovery['prefix_matches']['WH_Classic_Sk8brd_'])==5
scope='Five additional original entry points recover complete native Kill, class dispatch and auxiliary geometry enabling. Shared eight-operation selectors are specialized only for constant operation1; no other operations or whole shared helpers claimed. Sixteen Chromium suites pass, retaining the original prior training breakpoint and completed TR_startup. Real object deletion, rail/emitter/light/proximity changes and geometry collision state run; render dispatch still uses a test witness. Node indexes in Kill comparisons are fixture state. Separate original-only discovery constructs the real1917-node training indexes and finds the first five career-prefix targets; those builders are not yet lifted. No playable level, no further TR_Setup execution; main and separate17 physics build unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all sixteen suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=['scene-kill-draft.c','scene-kill-draft.wasm','scene-kill-draft.build.json','build-scene-kill-draft.py',
 'probe-scene-kill.py','scene-kill-fixtures.json','scene-kill-memory.bin','scene-kill-original.json','scene-kill-shared-coverage.json',
 'verify-scene-kill-checkpoint.mjs','scene-kill-browser.html','scene-kill-worker.mjs','serve-scene-kill.py','scene-kill-browser.json',
 'pin-scene-kill.py','audit-scene-kill.py','trace-training-node-index.py','training-node-index-discovery.json','node-build-instructions.txt',
 'node-index-ghidra.log','node-build-ghidra.log']
files+=['scene-kill-checkpoint-'+n+'-result.json' for n in names]
for directory in ['node-index-ghidra','node-build-ghidra']:
 files += [str(n.relative_to(p)) for n in sorted((p/directory).rglob('*')) if n.is_file()]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-lifetime-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':5,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':69,'unpromoted_functions_across_separate_experiments':86,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':16,'new_cases':148,'new_calls_including_existing_lifecycle':279,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
