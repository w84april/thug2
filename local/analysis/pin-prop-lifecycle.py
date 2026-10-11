"""Freeze the observed prop lifecycle checkpoint without rewriting old evidence."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis'
read=lambda x:json.loads(x.read_text())
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
proof_path=p/'prop-lifecycle-browser.json';pin_path=p/'prop-lifecycle-checkpoint.json'
assert not proof_path.exists() and not pin_path.exists()
prior_path=p/'composite-construction-checkpoint.json'
assert sha(prior_path)=='e14b50c8a6867e186ebf06b3b931a5617ddabb60887e8d7f60a7387ea3da8b96'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'prop-lifecycle-draft.build.json');module=p/'prop-lifecycle-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='7ba9f7606cd26c3fd95a9be5793fcbf392d7a885c237ebbc2c30287dc69c8b31'
assert module.stat().st_size==524639
names=['prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('prop-lifecycle-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n!='prop-lifecycle':assert suites[n.replace('-','_')]==read(p/('composite-construction-checkpoint-'+n+'-result.json'))
assert (suites['prop_lifecycle']['cases'],suites['prop_lifecycle']['calls'],suites['prop_lifecycle']['nan_fields_classification_only'])==(232,514,16)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='e46ea18c35715a61'
assert int(sys.argv[2])==len(canonical)==27667 and int(sys.argv[3])==len(candidate)==5
original=read(p/'prop-lifecycle-original.json');coverage=original['instruction_coverage']
assert len(coverage)==35 and original['cases']==232 and original['calls']==514
assert sum(len(c['missing']) for c in coverage.values())==22
assert all(set(c['missing'])==set(c['excluded']) for c in coverage.values())
assert all('allocation-failure epilogue' in why for c in coverage.values() for why in c['excluded'].values())
scope='Thirty-five additional original routines recover six prop component factories/constructors/destructors, Motion reset and node initialization, Suspend initialization/finalization/update, Sound proximity initialization and pending-owner/voice cleanup. Twenty-three actual Chromium suites pass, with all22 prior summaries unchanged. A constructed four-descriptor array runs the real shared builder and concrete factories/initializers before real destruction; it stops before Sound moved/finalization. Audio stop is an explicit platform-boundary observation callback with memory effects compared. Sixteen typed Suspend arithmetic NaNs use classification comparison; all other new comparisons are exact. Initialized services and successful heap allocations are contracts;22 allocation-failure epilogue instructions remain unexecuted. Partial component tables retain explicit zero unavailable slots. Full prop scripts, Sound update, scene creation/rendering and playable training remain. The main and separate physics builds are unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all23 suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['prop-lifecycle-draft.c','prop-lifecycle-draft.wasm','prop-lifecycle-draft.build.json','build-prop-lifecycle-draft.py',
 'probe-prop-lifecycle.py','prop-lifecycle-audio-probes.py','prop-lifecycle-audio-callback.c','prop-lifecycle-audio-callback.wasm','prop-lifecycle-audio-callback.build.json',
 'prop-lifecycle-fixtures.json','prop-lifecycle-memory.bin','prop-lifecycle-original.json','prop-lifecycle-function-instructions.txt',
 'prop-lifecycle-focus.tsv','prop-lifecycle-roots.txt','prop-sound-update-focus.tsv','prop-sound-update-roots.txt',
 'verify-prop-lifecycle-checkpoint.mjs','prop-lifecycle-browser.html','prop-lifecycle-worker.mjs','serve-prop-lifecycle.py',
 'prop-lifecycle-browser.json','pin-prop-lifecycle.py','audit-prop-lifecycle.py']
files+=['prop-lifecycle-checkpoint-'+n+'-result.json' for n in names]
for directory in ['prop-lifecycle-ghidra','prop-sound-update-ghidra']:
 files+=[directory+'.log']+[str(n.relative_to(p)) for n in sorted((p/directory).rglob('*')) if n.is_file()]
for n in files:
 if n!='prop-lifecycle-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/composite-construction-checkpoint.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':35,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':145,'unpromoted_functions_across_separate_experiments':162,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':23,'new_cases':232,'new_calls_including_existing_dependencies':514,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n')
assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
