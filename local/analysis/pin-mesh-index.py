"""Pin mesh index loading after original, Node and actual Chromium comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'mesh-index-checkpoint.json';proof_path=p/'mesh-index-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'scene-construction-checkpoint.json';assert sha(prior_path)=='e03cb6626518e7548fa326442babf0a5e02fa80508ac64342997ea92b7c569cf'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'mesh-index-draft.build.json');module=p/'mesh-index-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='7682796eaa9282bbbfa3b26032335cd52e0be3223a990efc781c6dfdbf4dd1c5'
assert module.stat().st_size==568510
for port,source in [('mesh-index-ports','mesh-index-ports.c'),('training-mesh-index-ports','mesh-index-ports.c'),('training-mesh-index-boundary','training-mesh-index-boundary.c')]:
 meta=read(p/(port+'.build.json'));assert sha(p/source)==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
 if 'included_source_sha256' in meta:assert meta['included_source_sha256']==sha(r/'tools/script_values_memory.c')
previous=read(p/'scene-construction-browser.json')['suites'];names=['mesh-index','training-mesh-index']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('mesh-index-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==46
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['mesh_index'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(102,186,3,0)
s=suites['training_mesh_index'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'mesh-index-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(102,186)
assert set(coverage)=={'0x4d4270','0x4d4300','0x4de420'}
assert sum(t['covered'] for t in coverage.values())==sum(t['total'] for t in coverage.values())==120
assert all(not t['missing'] for t in coverage.values())
training=read(p/'training-mesh-index-original.json');old_training=read(p/'training-scene-construction-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x4d5c30'
assert(training['partial_geometry_load']['covered_instructions'],training['partial_geometry_load']['total_instructions'])==(103,178)
assert(training['partial_sector_parser']['covered_instructions'],training['partial_sector_parser']['total_instructions'])==(222,346)
assert(training['partial_mesh_buffer']['covered_instructions'],training['partial_mesh_buffer']['total_instructions'])==(213,347)
assert training['io_calls']==old_training['io_calls'] and training['gpu_calls']==old_training['gpu_calls']
assert training['index_calls']=={'1':1,'2':1,'3':1} and training['crt_calls']=={'24':1,'272':1,'12':1}
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x4d5c30')
state=b['model_state'];assert {k:v for k,v in state.items() if k!='mesh'}==old_training['nodes'][1]['model_state']
mesh=state['mesh']
assert(mesh['flags'],mesh['material'],mesh['vertices'],mesh['stride'],mesh['indices'],mesh['vertex_bytes'],mesh['mesh_buffer_cursor_offset'])==('0x20040',state['materials']['material'],108,36,136,3888,501)
assert b['vertex_loader_request']=={'receiver':mesh['mesh'],'data':mesh['vertex_data'],'size':3888,'aux':'0x0'}
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-mesh-index-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap'];annotated.append((i,j))
assert annotated==[(1,10)]
unit=read(p/'mesh-index-fixtures.json');assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert len([n for n in unit['case_labels'] if n.startswith('overlap forward word copy')])==6
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Three complete routines recover index-buffer construction, lock/upload/unlock and material-value '
 'iteration.102 unit cases186 calls cover120/120 original instructions, including separate CRT '
 'allocation/registry linkage, ignored creation HRESULTs, failed/successful locks, odd copy sizes '
 'and overlapping forward word copies. CRT and GPU providers are explicit comparison boundaries. '
 'Two unchanged training cases22 calls include one interruption. Node204 completes; node1289 '
 'constructs its actual scene/mesh, loads and uploads all136 original indices, copies108 '
 'uncompressed vertices3888bytes and resolves the original material. Partial4c6650/4d5cc0 stop '
 'before4d5c30 vertex-buffer loading. Full mesh/parser completion and drawing are not fabricated. '
 'Arena, separate CRT arena/log, heap, globals, I/O, index and vertex bytes compare exactly after '
 'pointer relocation. Only the same28 proven uninitialized option bytes are masked in one '
 'interrupted training call; new suites have zero NaN allowances. Actual Chromium passes46 suites '
 'and all44 inherited summaries are identical. Vertex-buffer loading, complete meshes, production '
 'browser providers, rendering and playable gameplay remain pending. Main build unchanged.'
)

proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all46 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['mesh-index-draft.c','mesh-index-scene-derived.c','build-mesh-index-draft.py','mesh-index-draft.wasm','mesh-index-draft.build.json',
 'mesh-index-instructions.txt','probe-mesh-index.py','mesh-index-fixtures.json','mesh-index-memory.bin','mesh-index-original.json','mesh-index-probe.log',
 'mesh-index-ports-setup.py','mesh-index-ports.c','mesh-index-ports.wasm','mesh-index-ports.build.json','training-mesh-index-ports.wasm','training-mesh-index-ports.build.json',
 'probe-training-mesh-index.py','training-mesh-index-fixtures.json','training-mesh-index-memory.bin','training-mesh-index-original.json','training-mesh-index-probe.log',
 'training-mesh-index-boundary.c','training-mesh-index-boundary.wasm','training-mesh-index-boundary.build.json',
 'verify-mesh-index-checkpoint.mjs','mesh-index-full-node.log','mesh-index-browser.html','mesh-index-worker.mjs','serve-mesh-index.py',
 'mesh-index-browser.json','pin-mesh-index.py','audit-mesh-index.py']
files += ['mesh-index-checkpoint-'+n+'-result.json' for n in names]
files += ['vertex-buffer-ghidra.log']+[str(f.relative_to(p)) for f in sorted((p/'vertex-buffer-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='mesh-index-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/scene-construction-checkpoint.json','local/analysis/scene-construction-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':3,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':266,'unpromoted_functions_across_separate_experiments':283,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':46,'new_cases':104,'new_calls_including_existing_dependencies':208,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
