"""Pin verified original/Node/Chromium model asset file loading."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'model-asset-checkpoint.json';proof_path=p/'model-asset-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'texture-asset-checkpoint.json'
assert sha(prior_path)=='dc92e95f3368d68b75a08f5aa3e8484a5876bb9f88f3cde2b98fc85fbe914f84'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'model-asset-draft.build.json');module=p/'model-asset-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='1a451cfabdd90b314fee7bf26061c40718dc9eb2dac9d6621d96f34d15a24486'
assert module.stat().st_size==559138
for port in ['model-asset-ports','training-model-file-boundary','training-model-file-io']:
 meta=read(p/(port+'.build.json'));assert sha(p/(port+'.c'))==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
previous=read(p/'texture-asset-browser.json')['suites'];names=['model-asset','training-model-file']+[name.replace('_','-') for name in previous]
suites={name.replace('-','_'):read(p/('model-asset-checkpoint-'+name+'-result.json')) for name in names}
assert len(suites)==40
for name,summary in suites.items():
 assert summary['result']=='pass',name
 if name in previous:assert summary==previous[name],name
s=suites['model_asset'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(133,265,8,0)
s=suites['training_model_file'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'model-asset-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'],len(coverage))==(133,265,5)
assert sum(t['covered'] for t in coverage.values())==352 and sum(t['total'] for t in coverage.values())==354
for address,t in coverage.items():
 assert set(t['missing'])==set(t['excluded'])
 assert set(t['missing'])==({'0x40a0eb','0x40a0f1'} if address=='0x409eb0' else set())
assert original['io_calls']=={'0x5b7200':4,'0x3f00340':70,'0x5b6c60':72,'0x5b63a0':48,'0x5b6740':48,'0x5b7c00':12,'0x5b72e0':12}
training=read(p/'training-model-file-original.json')
assert(training['cases'],training['calls'])==(2,22)
assert training['partial_model_load']['complete'] is False and training['partial_configuration']['complete'] is False
assert training['partial_model_load']['boundary']=='0x48c030'
assert(training['model_file_coverage']['covered'],training['model_file_coverage']['total'])==(105,204)
assert training['io_calls']=={'0x5b6c60':2,'0x5b63a0':2,'0x5b6740':2,'0x5b68a0':1}
assert training['gpu_calls']=={'4':1,'1':1,'2':2,'3':2}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x48c030')
state=b['model_state'];assert(state['texture_asset']['state'],state['model_asset']['state'],state['model_asset']['pending_reads'])==(4,1,0)
assert state['model_asset']['bytes']==4710 and state['texture_asset']['mip_bytes']==[32,8]
assert b['model_buffer_request']=={'key':'0xe4dccfdf','data':state['model_asset']['buffer'],'arguments':[4710,0,int(state['texture_asset']['dictionary'],16),0,0,0]}
indeterminate=[1,2,3,12,13,14,15,18,19]+list(range(57,76));assert state['indeterminate_texture_option_bytes']==indeterminate
model=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.mdl.xbx'
assert sha(model)==training['model_file_sha256']=='6411a0aecbf3cf64068fea5cf04ebe971aaeb898bff6beb33d894eebe30c6dcf'
assert model.stat().st_size==training['model_file_bytes']==4710
fixture=read(p/'training-model-file-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4
    actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap']
   annotated.append((i,j))
assert annotated==[(1,10)]
unit=read(p/'model-asset-fixtures.json');assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Five complete model-asset routines recover option preparation, completion counting, source-buffer '
 'release and buffer/file load orchestration.133 unit cases265 calls cover352/354 instructions; the '
 'two excluded instructions require a file provider to mutate options17 after the loader resets it0. '
 'The unit suite instruments the parse virtual, explicitly checking file/cache/heap/state orchestration '
 'without fabricating geometry. It includes skin companion files, failures, low-byte flags, retained or '
 'copied buffers, fixed-pool aliasing, counter wrap and both asynchronous completion orders. '
 'Two real training cases22 calls include one interrupted call. Untouched scripts register1917 nodes; '
 'node204 completes and node1289 loads the real texture plus all4710 bytes of Letter_S.mdl.xbx. '
 'Partial409c70 then resolves the actual texture dependency and reaches missing48c030 with all eight '
 'parser arguments verified. No complete409c70,4935e0 or geometry routine is claimed. Complete arena, '
 'heap, I/O and mip data compare after pointer relocation. Only28 proven uninitialized option bytes '
 'are masked in the interrupted training call; units check all fixed-pool bytes exactly. Both new '
 'suites have zero NaN allowances. Ordinary file, cached file, allocator and GPU providers are explicit '
 'comparison boundaries. Actual Chromium passes40 suites, all38 previous summaries remain identical. '
 'Model geometry, texture/model destruction, production browser providers and playable rendering '
 'remain pending. Main and separate physics builds remain unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all40 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['model-asset-extension.c','model-asset-texture-derived.c','model-asset-factory-derived.c','build-model-asset-draft.py','model-asset-draft.wasm','model-asset-draft.build.json','model-asset-instructions.txt',
 'probe-model-asset.py','model-asset-fixtures.json','model-asset-memory.bin','model-asset-original.json','model-asset-probe.log',
 'probe-training-model-file.py','training-model-file-ports-setup.py','training-model-file-fixtures.json','training-model-file-memory.bin','training-model-file-original.json','training-model-file-probe.log',
 'verify-model-asset-checkpoint.mjs','model-asset-full-node.log','model-asset-browser.html','model-asset-worker.mjs','serve-model-asset.py','model-asset-browser.json','pin-model-asset.py','audit-model-asset.py',
 'model-buffer-ghidra.log','model-geometry-ghidra.log']
files += [port+suffix for port in ['model-asset-ports','training-model-file-boundary','training-model-file-io'] for suffix in ['.c','.wasm','.build.json']]
files += ['model-asset-checkpoint-'+name+'-result.json' for name in names]
for directory in ['model-buffer-ghidra','model-geometry-ghidra']:files += [str(f.relative_to(p)) for f in sorted((p/directory).rglob('*')) if f.is_file()]
for name in files:
 if name!='model-asset-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/texture-asset-checkpoint.json','local/analysis/texture-asset-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':5,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':252,'unpromoted_functions_across_separate_experiments':269,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':40,'new_cases':135,'new_calls_including_existing_dependencies':287,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_model_load':training['partial_model_load'],'indeterminate_option_bytes':indeterminate,
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
