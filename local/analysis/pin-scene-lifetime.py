"""Freeze the observed scene-lifetime checkpoint once only."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';read=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'scene-lifetime-browser.json';pin_path=p/'scene-lifetime-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior=read(p/'scene-state-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'scene-lifetime-draft.build.json');module=p/'scene-lifetime-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='74692f21d3cfe6f90b155355fb4fc778411b6fdb89ce5d851b9db467ee32fcff'
names=['scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('scene-lifetime-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 assert suites[n.replace('-','_')]==read(p/((n+'-result.json') if n in names[:3] else ('scene-state-checkpoint-'+n+'-result.json')))
assert [(suites[n]['cases'],suites[n]['calls']) for n in ['scene_subscribe','scene_lifetime','scene_proximity']]==[(50,178),(90,290),(131,567)]
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'
assert int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
originals=[read(p/(n+'-original.json')) for n in names[:3]]
coverage={k:v for original in originals for k,v in original['instruction_coverage'].items()}
assert len(coverage)==11 and sum(c['total'] for c in coverage.values())==333
assert sum(c['covered'] for c in coverage.values())==330
assert {a for c in coverage.values() for a in c['missing']}=={'0x46268b','0x4633e1','0x463417'}
scope='Eleven additional original routines recover guarded/direct and deferred object deletion, Kill callback, dead queue insertion/flushing and native FlushDeadObjects, event-listener append/subscription/wait and proximity shutdown. Real registered base-object destruction, nested traversal/removal, constructed owned-script cleanup and actual cached-QB spawning execute without gameplay callback substitutes. Fifteen actual Chromium suites pass, retaining completed TR_startup and the prior TR_Setup breakpoint before Kill. Concrete skater destruction, whole Kill/scene dispatch, loading node indexes and production browser services remain. No playable level; main and separate17 physics build unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all fifteen suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=['scene-lifetime-draft.c','scene-lifetime-draft.wasm','scene-lifetime-draft.build.json','build-scene-lifetime-draft.py',
 'scene-lifetime-oracle.py','scene-lifetime-fixture-setup.py','verify-scene-lifetime.mjs','verify-scene-lifetime-checkpoint.mjs',
 'scene-lifetime-browser.html','scene-lifetime-worker.mjs','serve-scene-lifetime.py','scene-lifetime-browser.json','pin-scene-lifetime.py','audit-scene-lifetime.py',
 'scene-lifetime-dependencies-instructions.txt','kill-operation-instructions.txt']
for n in names[:3]:files+=['probe-'+n+'.py',n+'-fixtures.json',n+'-memory.bin',n+'-original.json',n+'-result.json']
files+=['scene-lifetime-checkpoint-'+n+'-result.json' for n in names]
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-state-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':11,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':64,'unpromoted_functions_across_separate_experiments':81,
 'specimen_sha256':originals[0]['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':15,'new_cases':271,'new_calls_including_existing_lifecycle':1035,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
