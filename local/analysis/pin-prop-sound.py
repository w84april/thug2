"""Preserve the observed Sound/common-training-components checkpoint."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();read=lambda x:json.loads(x.read_text())
pin_path=p/'prop-sound-checkpoint.json';proof_path=p/'prop-sound-browser.json'
assert not pin_path.exists() and not proof_path.exists()
prior_path=p/'prop-lifecycle-checkpoint.json'
assert sha(prior_path)=='ec311e249d251fcde9e9e17e233c25922f2cf5a5db55b59a9a196c46d5bb366e'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'prop-sound-draft.build.json');module=p/'prop-sound-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='c77e61e3d8ffdca4a83153ec396b912c0fc80f8fb7a2ae137ce88560c8c242ea'
assert module.stat().st_size==532415
names=['prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('prop-sound-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('prop-lifecycle-checkpoint-'+n+'-result.json'))
assert (suites['prop_sound']['cases'],suites['prop_sound']['calls'],suites['prop_sound']['nan_fields_classification_only'])==(331,569,0)
assert (suites['training_prop_components']['cases'],suites['training_prop_components']['calls'])==(1,128)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'=='7441394db0ea369f'
assert int(sys.argv[2])==len(canonical)==30153 and int(sys.argv[3])==len(candidate)==5
original=read(p/'prop-sound-original.json');coverage=original['instruction_coverage']
assert len(coverage)==21 and all(c['covered']==c['total'] and not c['missing'] for c in coverage.values())
training=read(p/'training-prop-components-original.json');assert training['nodes']==1917 and len(training['props'])==61
inventory=read(p/'training-scene-node-inventory.json')
assert next(c['nodes'] for c in inventory['classes'] if c['text']=='GameObject')==61
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
scope='Twenty-one additional routines recover Sound update, complete queue/play wrapper, owner registration/lookup and spatial geometry dependencies. All25 actual Chromium suites pass; all23 old summaries are unchanged. The untouched object.qb, skutils.qb and TR.qb load and all1917 nodes register; all61 Class=GameObject nodes drive actual four-component construction, initialization, finalization/moved and destruction. Full30MiB training state, globals, allocation effects and preserved registers compare. All new comparisons are exact, with no NaN allowances. Initialized service state, supported volume shapes and an available camera for due queued sounds are contracts: original unsupported shape/no-camera retry paths read uninitialized stack results, and the new code traps rather than supplying invented output. OS audio and CRT services remain explicit test boundaries, not browser playback implementations. Complete468cb0 scripted assembly, model/animation/collision components, triggers, scene rendering and playable training remain. Main and separate physics builds are unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all25 suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['prop-sound-draft.c','prop-sound-lifecycle-derived.c','prop-sound-draft.wasm','prop-sound-draft.build.json','build-prop-sound-draft.py',
 'probe-prop-sound.py','prop-sound-fixtures.json','prop-sound-memory.bin','prop-sound-original.json',
 'prop-sound-audio-callbacks.wasm','prop-sound-audio-callbacks.build.json','prop-sound-function-instructions.txt','prop-sound-support-instructions.txt','prop-sound-support-focus.tsv',
 'probe-training-prop-components.py','training-prop-components-fixtures.json','training-prop-components-memory.bin','training-prop-components-original.json',
 'inspect-gameobj-script.mjs','gameobj-add-components-script.json','verify-prop-sound-checkpoint.mjs',
 'prop-sound-browser.html','prop-sound-worker.mjs','serve-prop-sound.py','prop-sound-browser.json','pin-prop-sound.py','audit-prop-sound.py']
files+=['prop-sound-checkpoint-'+n+'-result.json' for n in names]
files+=['prop-sound-support-ghidra.log']+[str(n.relative_to(p)) for n in sorted((p/'prop-sound-support-ghidra').rglob('*')) if n.is_file()]
for n in files:
 if n!='prop-sound-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/prop-lifecycle-checkpoint.json','tools/audio_device_callbacks.c'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':21,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':166,'unpromoted_functions_across_separate_experiments':183,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':25,'new_cases':332,'new_calls_including_existing_dependencies':697,'actual_training_gameobjects_common_components':61,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
