"""Preserve the observed prop-command/training-script checkpoint."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();read=lambda x:json.loads(x.read_text())
pin_path=p/'prop-command-checkpoint.json';proof_path=p/'prop-command-browser.json'
assert not pin_path.exists() and not proof_path.exists()
prior_path=p/'prop-sound-checkpoint.json'
assert sha(prior_path)=='192929403e3b6c99852ac8b17f941726563f1134bb76d94ecb818d45eaf4beca'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in prior[group].items():assert sha(r/n)==h,(group,n)
build=read(p/'prop-command-draft.build.json');module=p/'prop-command-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for n,h in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/n)==h,n
assert sha(module)==build['sha256']=='537f68fb047e32d8d138c5f2758f86c9d08c52d287558610dc8013e2cf930ca5'
assert module.stat().st_size==538204
names=['prop-command','training-prop-script','prop-sound','training-prop-components','prop-lifecycle','composite-math','composite-construction','node-registration','training-node-registration','node-index','training-node-index','scene-kill','scene-subscribe','scene-lifetime','scene-proximity','scene-state','scene-disposal','scene-visitor','training-mode','node-prefix','scene-name','training-setup','asset-factory','training-load','skeleton-asset','skeleton-buffer','script-change']
suites={n.replace('-','_'):read(p/('prop-command-checkpoint-'+n+'-result.json')) for n in names}
for n in names:
 assert suites[n.replace('-','_')]['result']=='pass'
 if n not in names[:2]:assert suites[n.replace('-','_')]==read(p/('prop-sound-checkpoint-'+n+'-result.json'))
assert (suites['prop_command']['cases'],suites['prop_command']['calls'],suites['prop_command']['nan_fields_classification_only'])==(248,562,0)
assert (suites['training_prop_script']['cases'],suites['training_prop_script']['calls'],suites['training_prop_script']['nan_fields_classification_only'])==(2,22,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for c in canonical:h=((h^ord(c))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}'
assert int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'prop-command-original.json');coverage=original['instruction_coverage']
assert len(coverage)==22 and sum(c['covered'] for c in coverage.values())==861 and sum(c['total'] for c in coverage.values())==872
for c in coverage.values():assert set(c['missing'])==set(c.get('excluded',{}))
training=read(p/'training-prop-script-original.json');assert training['cases']==2 and training['calls']==22
assert training['nodes'][0]['node_index']==204 and training['nodes'][0]['execute_result']==0 and training['nodes'][0]['final_instruction']=='0x0'
assert training['nodes'][1]['node_index']==1289 and training['nodes'][1]['first_missing_factory']=='0x421490'
assert training['nodes'][1]['native_entries']['0x45d810']==1 and training['nodes'][1]['native_entries']['0x45d850']==1
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
scope='Twenty-two additional routines recover composite command dispatch, object parameter/event changes and three native script predicates with their text-getter dependency. All27 actual Chromium suites pass; all25 prior summaries are unchanged. Untouched object.qb/skutils.qb/ped.qb/TR.qb load and all1917 nodes register in each new integration case. Actual training node204 completes gameobj_add_components with result0 and no optional component. Node1289, the SKATE letter S, executes actual member dispatch and stops before model factory421490. That explicit test-only factory trap provides no component or success. At the breakpoint the host interpreter service scope remains active and its stack location and contents are verified; normal returns must restore the caller scope. New comparisons cover250 cases584 calls and full arenas/globals/allocation effects with no NaN allowances. Instruction coverage861/872 includes11 explicit exclusions for process bootstrap, alignment and allocation failure outside the initialized live-object contract; event-parameter selected-pool exhaustion is tested. Original missing required strings read uninitialized stack pointers; the recovered routine traps instead. Full468cb0 assembly, missing model/animation/collision factories and methods, triggers, rendering and playable training remain. Main and separate physics builds are unchanged.'
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all27 suite summaries and full DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['prop-command-draft.c','prop-command-composite-derived.c','prop-command-draft.wasm','prop-command-draft.build.json','build-prop-command-draft.py',
 'probe-prop-command.py','prop-command-dispatch-probes.py','prop-predicate-probes.py','prop-command-fixtures.json','prop-command-memory.bin','prop-command-original.json','prop-command-probe.log',
 'prop-command-callback.c','prop-command-callback.wasm','prop-command-callback.build.json','prop-command-instructions.txt','prop-command-support-instructions.txt','prop-command-event-instructions.txt','prop-command-focus.tsv',
 'prop-script-predicates-instructions.txt','prop-script-factory-discovery.json',
 'probe-training-prop-script.py','training-prop-script-fixtures.json','training-prop-script-memory.bin','training-prop-script-original.json','training-prop-script-probe.log',
 'training-prop-script-boundary.c','training-prop-script-boundary.wasm','training-prop-script-boundary.build.json','training-prop-script-checks.mjs',
 'discover-prop-script-nodes.py','training-prop-script-node-discovery.json','verify-prop-command-checkpoint.mjs','prop-command-full-node.log',
 'prop-command-browser.html','prop-command-worker.mjs','serve-prop-command.py','prop-command-browser.json','pin-prop-command.py','audit-prop-command.py']
files+=['prop-command-checkpoint-'+n+'-result.json' for n in names]
files+=['prop-command-ghidra.log']+[str(n.relative_to(p)) for n in sorted((p/'prop-command-ghidra').rglob('*')) if n.is_file()]
for n in files:
 if n!='prop-command-browser.json':assert (p/n).is_file(),n
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/prop-sound-checkpoint.json','local/analysis/prop-sound-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':22,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':188,'unpromoted_functions_across_separate_experiments':205,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':27,'new_cases':250,'new_calls_including_existing_dependencies':584,'actual_training_prop_script_cases':2,
 'instruction_coverage':coverage,'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
pin_path.write_text(json.dumps(pin,indent=2)+'\n');assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(pin_path),'main_unchanged':True}))
