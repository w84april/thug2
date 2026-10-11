"""Pin original, Node and observed Chromium texture-asset comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'texture-asset-checkpoint.json';proof_path=p/'texture-asset-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'texture-buffer-checkpoint.json'
assert sha(prior_path)=='164a59600982b90c874339f161badf29aacafb192822ce6663b6cacaba16214e'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'texture-asset-draft.build.json');module=p/'texture-asset-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='31306c2a8c682edb648108b025fc5409d17826dd0443b51eb0008597572b08f0'
assert module.stat().st_size==556038
for port in ['boundary','gpu','io']:
 meta=read(p/('training-texture-'+port+'.build.json'))
 assert sha(p/('training-texture-'+port+'.c'))==meta['source_sha256']
 assert sha(p/('training-texture-'+port+'.wasm'))==meta['sha256']
previous=read(p/'texture-buffer-browser.json')['suites'];names=['texture-asset','training-texture-asset']+[name.replace('_','-') for name in previous]
suites={name.replace('-','_'):read(p/('texture-asset-checkpoint-'+name+'-result.json')) for name in names}
assert len(suites)==38
for name,summary in suites.items():
 assert summary['result']=='pass',name
 if name in previous:assert summary==previous[name],name
s=suites['texture_asset'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(91,206,13,0)
s=suites['training_texture_asset'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'texture-asset-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'],len(coverage))==(91,206,9)
assert sum(t['covered'] for t in coverage.values())==sum(t['total'] for t in coverage.values())==352
for t in coverage.values():assert not t['missing'] and not t['excluded']
assert original['gpu_calls']=={'1':22,'2':44,'3':44}
assert original['io_calls']=={'0x5b6c60':16,'0x5b63a0':10,'0x5b6740':10,'0x5b68a0':10}
assert len(original['assets'])==20 and all(a['state']==4 and a['gpu_events']==5 for a in original['assets'])
training=read(p/'training-texture-asset-original.json')
assert(training['cases'],training['calls'])==(2,22)
assert training['partial_model_load']['complete'] is False
assert(training['partial_model_load']['covered_instructions'],training['partial_model_load']['total_instructions'])==(101,236)
assert training['partial_model_load']['boundary']=='0x409eb0'
assert training['partial_configuration']['complete'] is False
assert training['gpu_calls']=={'4':1,'1':1,'2':2,'3':2}
assert training['io_calls']=={'0x5b6c60':1,'0x5b63a0':1,'0x5b6740':1,'0x5b68a0':1}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x409eb0')
assert b['model_file_request']['path']=='models\\gameobjects\\skate\\letter_s\\letter_s.mdl'
assert b['model_file_request']['arguments']==[0]*7+[46]
assert b['model_state']['texture_asset']['state']==4 and b['model_state']['texture_asset']['mip_bytes']==[32,8]
assert b['model_state']['indeterminate_texture_option_bytes']==[1,2,3]+list(range(57,76))
letter=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.tex.xbx'
assert sha(letter)==training['texture_file_sha256']=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
assert letter.stat().st_size==88
# Exact exception: only the originally uninitialized bytes copied from4935e0's
# automatic texture options. Every defined field and every other byte is exact.
fixture=read(p/'training-texture-asset-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4
    actual[offset]=mask
   assert actual=={0:255,56:255,60:0,64:0,68:0,72:0} and step['expected_trap']
   annotated.append((i,j))
assert annotated==[(1,10)]
unit=read(p/'texture-asset-fixtures.json')
assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Nine additional complete routines recover fixed asset-option allocation/release, texture asset options, '
 'filename formatting, buffer/file loading, parsing, model basename stripping and model-option initialization. '
 'All352 original instructions execute across91 cases206 calls; four previously recovered dependencies '
 'are exercised but not counted again. Two additional training cases22 calls include one explicit interrupted '
 'call. Untouched training scripts register1917 nodes; node204 completes, while node1289 loads the real '
 '88-byte Letter S texture through the actual manager, factory, synchronous file loader, dictionary parser '
 'and cache. It creates the dependent model asset and stops before unrecovered409eb0 model-file loading. '
 'Partial4935e0 covers101/236 instructions and is not counted complete. Arena, heap, file/GPU arguments '
 'and two32/8-byte mip uploads compare exactly after pointer relocation. Only22 originally uninitialized '
 'bytes copied into the first texture-option slot are masked in the interrupted training comparison; '
 'unit options retain exact whole-storage checks. There are zero NaN allowances in either new suite. '
 'File I/O, heap-owner query and GPU create/lock/unlock are explicit comparison ports. They do not '
 'constitute production browser providers or rendering. Actual Chromium passes38 suites and all36 '
 'inherited summaries remain identical. Texture destruction, complete model loading, model drawing '
 'and the playable level remain pending. Main and separate physics builds remain unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all38 suite summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['texture-asset-extension.c','texture-asset-factory-derived.c','texture-asset-configuration-derived.c','model-texture-load-prefix.c',
 'build-texture-asset-draft.py','texture-asset-draft.wasm','texture-asset-draft.build.json','texture-asset-instructions.txt',
 'probe-texture-asset.py','texture-asset-fixtures.json','texture-asset-memory.bin','texture-asset-original.json','texture-asset-probe.log',
 'probe-training-texture-asset.py','training-texture-ports-setup.py','training-texture-asset-fixtures.json','training-texture-asset-memory.bin',
 'training-texture-asset-original.json','training-texture-asset-probe.log','training-texture-asset-checks.mjs',
 'verify-texture-asset-checkpoint.mjs','texture-asset-full-node.log','texture-asset-browser.html','texture-asset-worker.mjs',
 'serve-texture-asset.py','texture-asset-browser.json','pin-texture-asset.py','audit-texture-asset.py']
files += ['training-texture-'+port+suffix for port in ['boundary','gpu','io'] for suffix in ['.c','.wasm','.build.json']]
files += ['texture-asset-checkpoint-'+name+'-result.json' for name in names]
for name in files:
 if name!='texture-asset-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/texture-buffer-checkpoint.json','local/analysis/texture-buffer-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':9,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':247,'unpromoted_functions_across_separate_experiments':264,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,
 'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':38,'new_cases':93,'new_calls_including_existing_dependencies':228,
 'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],'instruction_coverage':coverage,
 'partial_model_load':training['partial_model_load'],'indeterminate_texture_option_bytes':[1,2,3]+list(range(57,76)),
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},
 'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
