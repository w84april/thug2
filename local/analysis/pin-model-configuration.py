"""Pin observed original/Node/Chromium model-configuration progress."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
target=p/'model-configuration-checkpoint.json';proof_path=p/'model-configuration-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'model-initialize-checkpoint.json'
assert sha(prior_path)=='93dd2f3e00c0e49b2565b97e50541fdae96780e14cad96bf70da14ffe3d65d98'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'model-configuration-draft.build.json');module=p/'model-configuration-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
for name,digest in build['derived_from'].items():assert prior['artifact_hashes'][name]==digest,name
assert sha(module)==build['sha256']=='9b2b2171f060196718aafbf6d47ed1a0cde5cd91b16504e4eccd63dfe8e575a1'
assert module.stat().st_size==549534
previous=read(p/'model-initialize-browser.json')['suites']
names=['model-configuration','model-configuration-prefix','training-model-configuration']+[name.replace('_','-') for name in previous]
suites={name.replace('-','_'):read(p/('model-configuration-checkpoint-'+name+'-result.json')) for name in names}
assert len(suites)==35
for name,summary in suites.items():
 assert summary['result']=='pass',name
 if name in previous:assert summary==previous[name],name
for name,cases,calls in [('model_configuration',216,289),('model_configuration_prefix',36,198),('training_model_configuration',2,22)]:
 s=suites[name];assert (s['cases'],s['calls'],s['nan_fields_classification_only'])==(cases,calls,0)
assert suites['model_configuration']['signaling_nan_words_quieted_per_x87']==16
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'model-configuration-original.json');coverage=original['instruction_coverage']
assert (original['cases'],original['calls'])==(216,289)
assert len(coverage)==14 and sum(c['covered'] for c in coverage.values())==387 and sum(c['total'] for c in coverage.values())==392
for item in coverage.values():assert set(item['missing'])==set(item['excluded'])
prefix=read(p/'model-configuration-prefix-original.json');training=read(p/'training-model-configuration-original.json')
assert (prefix['cases'],prefix['calls'])==(36,198)
assert prefix['instruction_coverage']=={}
assert prefix['partial_initializer']['covered_instructions']==69 and prefix['partial_initializer']['total_instructions']==74
assert prefix['partial_initializer']['boundary']=='0x4935e0' and prefix['partial_initializer']['interrupted_calls']==36
config=prefix['partial_configuration']
assert (config['address'],config['boundary'],config['covered_instructions'],config['total_instructions'],config['complete'])==('0x420d10','0x4935e0',142,396,False)
assert len(set(config['executed']))==142 and config['executed'][-1]=='0x42118c'
assert (training['cases'],training['calls'])==(2,22)
assert training['nodes'][0]['execute_result']==0 and training['nodes'][0]['final_instruction']=='0x0'
node=training['nodes'][1];assert node['node_index']==1289 and node['first_missing_routine']=='0x4935e0'
assert node['interrupted_calls']==1 and node['completed_calls']==10
assert node['model_state']['owner_components']==['0xce0ca665','0xa015e17','0x1d5b1ae6','0x7713c7b','0x286a8d26']
assert node['model_load_request']['path']=='models\\gameobjects\\skate\\letter_s\\letter_s.mdl'
assert node['model_load_request']['arguments']==[int(node['model_state']['renderer'],16),0,1,0,0,0,1,0]
for a in ['0x4214f0','0x420d10','0x494ba0','0x487b00','0x487a70','0x402080']:assert node['native_entries'][a]==1
assert training['partial_configuration']['covered_instructions']==124
assert set(training['partial_configuration']['executed'])<=set(config['executed'])
assert original['specimen_sha256']==prefix['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Fourteen additional original routines recover base and PC geometry construction, base geometry lifetime, '
 'list range erasure, virtual geometry/texture release, renderer reset, scale parsing/flags and model path preparation. '
 'Reset tests use actual base geometry destructors for concrete virtual objects; PC mesh destruction and asset loading '
 'are still unavailable. Full helper instruction coverage387/392 excludes only five geometry allocation-failure '
 'instructions under the explicit successful-allocation contract. New254 cases509 calls include37 interrupted calls; '
 'new comparisons have zero NaN classification allowances. Sixteen signaling-NaN output words require the exact x87 '
 'quiet bit with sign/payload retained. All35 Chromium suites pass; all32 prior summaries are unchanged. '
 'The initializer4214f0 remains partial69/74. Configuration420d10 implements only its text-model path to4935e0, '
 'with142/396 original instructions exercised across36 controlled cases. Alternate source branches and post-load tail '
 'trap as unavailable. Neither partial function is counted as completely recovered. The pending asset-loader callback '
 'records component, parameters, renderer, normalized path and all defined loader arguments, then traps without a '
 'replacement result. Whole arena/global/heap comparisons and active direct/interpreter service scopes are checked. '
 'The untouched training scripts register all1917nodes percase; node204 completes, while node1289 SKATE letter S reaches '
 'the actual model-load request for models\\gameobjects\\skate\\letter_s\\letter_s.mdl. No asset has been loaded by '
 'that request and no model is rendered; the level is not playable. Main and separate physics builds remain unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],
 'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all35 suite summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['model-configuration-draft.c','model-configuration-initialize-derived.c','build-model-configuration-draft.py',
 'model-configuration-draft.wasm','model-configuration-draft.build.json','model-configuration-focus.tsv',
 'model-configuration-discovery.txt','model-configuration-instructions.txt','model-configuration-methods.json',
 'verify-model-configuration-checkpoint.mjs','model-configuration-full-node.log','model-configuration-browser.html',
 'model-configuration-worker.mjs','serve-model-configuration.py','model-configuration-browser.json',
 'pin-model-configuration.py','audit-model-configuration.py','model-configuration-ghidra.log']
for name in names[:3]:
 files += ['probe-'+name+'.py',name+'-fixtures.json',name+'-memory.bin',name+'-original.json',name+'-probe.log']
for name in names[1:3]:files += [name+'-boundary.c',name+'-boundary.wasm',name+'-boundary.build.json']
files += ['model-configuration-checkpoint-'+name+'-result.json' for name in names]
files += [str(f.relative_to(p)) for f in sorted((p/'model-configuration-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='model-configuration-browser.json':assert (p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/model-initialize-checkpoint.json','local/analysis/model-initialize-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':14,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':229,'unpromoted_functions_across_separate_experiments':246,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,
 'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':35,'new_cases':254,'new_calls_including_existing_dependencies':509,
 'new_interrupted_calls':37,'actual_training_model_configuration_cases':2,'instruction_coverage':coverage,
 'partial_initializer_not_counted_as_complete':prefix['partial_initializer'],'partial_configuration_not_counted_as_complete':config,
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
