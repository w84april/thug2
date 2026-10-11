"""Freeze vertex upload after original, Node and actual Chromium comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'vertex-upload-checkpoint.json';proof_path=p/'vertex-upload-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'mesh-index-checkpoint.json';assert sha(prior_path)=='aa6a2c6af5c8c0a0f1ef1ac4c017d354b87ba467055136d410f94468a877a8aa'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'vertex-upload-draft.build.json');module=p/'vertex-upload-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='e3dc9be10e0468751a3580ebb7069ee1a8d63415ec88be163837fb8c9eb95d94'
assert module.stat().st_size==571396
for port,source in [('vertex-upload-ports','vertex-upload-ports.c'),('training-vertex-upload-ports','vertex-upload-ports.c'),('training-vertex-upload-boundary','training-vertex-upload-boundary.c')]:
 meta=read(p/(port+'.build.json'));assert sha(p/source)==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
 if 'included_source_sha256' in meta:assert meta['included_source_sha256']==sha(r/'tools/script_values_memory.c')
previous=read(p/'mesh-index-browser.json')['suites'];names=['vertex-upload','training-vertex-upload']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('vertex-upload-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==48
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['vertex_upload'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(377,679,7,0)
s=suites['training_vertex_upload'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'vertex-upload-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(377,679)
assert set(coverage)=={'0x4d3ff0','0x4d40e0','0x4d5760','0x4d5c30','0x4d3ed0','0x4da710'}
assert sum(t['covered'] for t in coverage.values())==sum(t['total'] for t in coverage.values())==270
assert all(not t['missing'] for t in coverage.values())
training=read(p/'training-vertex-upload-original.json');old_training=read(p/'training-mesh-index-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x4d5900'
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
assert (training['partial_mesh_buffer']['covered_instructions'],training['partial_mesh_buffer']['total_instructions'])==(248,347)
assert (training['partial_sector_parser']['covered_instructions'],training['partial_sector_parser']['total_instructions'])==(232,346)
assert training['partial_mesh_buffer']['covered_instructions']>old_training['partial_mesh_buffer']['covered_instructions']
assert training['partial_sector_parser']['covered_instructions']>old_training['partial_sector_parser']['covered_instructions']
assert training['io_calls']==old_training['io_calls'] and training['gpu_calls']==old_training['gpu_calls']
assert training['index_calls']=={'1':2,'2':2,'3':2} and training['crt_calls']=={'24':1,'272':1,'12':2,'36':1,'3888':1}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x4d5900')
state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k!='mesh'}=={k:v for k,v in old_state.items() if k!='mesh'}
mesh=state['mesh'];assert all(mesh[k]==v for k,v in old_state['mesh'].items())
assert(mesh['vertex_wrapper'],mesh['cpu_vertices'],mesh['gpu_vertices'],mesh['vertex_registry'],mesh['shader_handle'],mesh['vertex_stream_released'])==('0x2900164','0x2900198','0x2b08100','0x29010d8','0x0',True)
assert b['bounds_request']=={'receiver':mesh['mesh']}
for fn in ['0x4d5c30','0x4d5760','0x4d3ff0','0x4d40e0','0x4d3ed0']:assert b['native_entries'][fn]==1
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-vertex-upload-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap'];annotated.append((i,j))
assert annotated==[(1,10)]
# Rebuild the final comparison arena, verify every original vertex byte at both
# CPU and explicit GPU destinations, and prove the temporary stream was freed.
arena=bytearray((p/fixture['memory']).read_bytes());base=fixture['base'];case=fixture['cases'][1]
for address,data in case.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
for step in case['steps']:
 for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:int.from_bytes(arena[a-base:a-base+4],'little')
model=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
for key in ['cpu_vertices','gpu_vertices']:
 at=int(mesh[key],16);assert arena[at-base:at-base+3888]==model[798:4686]
context=0x1000020;assert word(context)==int(mesh['vertex_data'],16)-16
last=word(context+12)+(word(context+8)-1)*48;assert word(last)==2 and word(last+4)==int(mesh['vertex_data'],16)
unit=read(p/'vertex-upload-fixtures.json');assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert len([n for n in unit['case_labels'] if n.startswith('overlap forward word copy')])==6
assert len([n for n in unit['case_labels'] if n.startswith('callback changes live fields')])==2
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Six complete routines recover vertex-buffer construction/allocation, upload/unlock, mesh vertex '
 'loading, shader handle selection and PC shader-record skipping.377 unit cases679 calls cover '
 '270/270 original instructions, including null outer allocation, independent GPU/CPU suppression, '
 'creation and lock errors, direct Unlock HRESULTs, deferred GPU owners, alignment, overlap and '
 'callback changes to live fields. Existing4d4090 lock is included in18 integration cases. '
 'Two training cases22 calls include one interruption. Node204 completes; node1289 loads and uploads '
 'all108 original vertices3888bytes after136indices, resolves the material, selects the current '
 'shader handle and releases its temporary stream. The standard4d5cc0 branch returns, then partial '
 '4c6650 stops before4d5900 mesh bounds. Compressed/alternate/conversion paths remain explicit traps. '
 'Arena, CRT arena/log, heap, globals, I/O and CPU/GPU bytes compare after pointer relocation. '
 'Only the same28 proven uninitialized option bytes are masked; no new NaN allowances. Actual '
 'Chromium passes48 suites with46 inherited summaries identical. CRT/GPU providers are comparison '
 'fixtures, and shader initialization is still pending. Full meshes, rendering and playable gameplay '
 'remain unfinished. Main build unchanged.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all48 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['vertex-upload-draft.c','vertex-upload-mesh-derived.c','build-vertex-upload-draft.py','vertex-upload-draft.wasm','vertex-upload-draft.build.json',
 'vertex-upload-instructions.txt','vertex-upload-inspection.txt','probe-vertex-upload.py','vertex-upload-fixtures.json','vertex-upload-memory.bin','vertex-upload-original.json','vertex-upload-probe.log',
 'vertex-upload-ports-setup.py','vertex-upload-ports.c','build-vertex-upload-ports.py','vertex-upload-ports.wasm','vertex-upload-ports.build.json','training-vertex-upload-ports.wasm','training-vertex-upload-ports.build.json',
 'probe-training-vertex-upload.py','training-vertex-upload-fixtures.json','training-vertex-upload-memory.bin','training-vertex-upload-original.json','training-vertex-upload-probe.log',
 'training-vertex-upload-boundary.c','training-vertex-upload-boundary.wasm','training-vertex-upload-boundary.build.json',
 'verify-vertex-upload-checkpoint.mjs','vertex-upload-full-node.log','vertex-upload-browser.html','vertex-upload-worker.mjs','serve-vertex-upload.py',
 'vertex-upload-browser.json','pin-vertex-upload.py','audit-vertex-upload.py']
files += ['vertex-upload-checkpoint-'+n+'-result.json' for n in names]
for name in files:
 if name!='vertex-upload-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/mesh-index-checkpoint.json','local/analysis/mesh-index-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':6,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':272,'unpromoted_functions_across_separate_experiments':289,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':48,'new_cases':379,'new_calls_including_existing_dependencies':701,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
