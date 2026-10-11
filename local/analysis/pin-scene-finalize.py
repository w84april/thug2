"""Freeze scene finalization after original, Node and actual Chromium comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'scene-finalize-checkpoint.json';proof_path=p/'scene-finalize-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'mesh-register-checkpoint.json';assert sha(prior_path)=='cbde75891bc84177d16984ec736d85d8731b0c6041a0f892fbf2a75d075aa3c6'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'scene-finalize-draft.build.json');module=p/'scene-finalize-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='72522d1ebfddcd9f764068d8c9ae588a7a7ac72a9bc8fb33f7c478b3043ab75b'
assert module.stat().st_size==578707
for port in ['scene-finalize-ports','training-scene-finalize-boundary']:
 meta=read(p/(port+'.build.json'));assert sha(p/(port+'.c'))==meta['source_sha256'] and sha(p/(port+'.wasm'))==meta['sha256']
previous=read(p/'mesh-register-browser.json')['suites'];names=['scene-finalize','training-scene-finalize']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('scene-finalize-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==52
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['scene_finalize'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(311,613,17,0)
s=suites['training_scene_finalize'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'scene-finalize-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(311,613)
assert len(coverage)==18
assert sum(t['covered'] for t in coverage.values())==551 and sum(t['total'] for t in coverage.values())==555
excluded={'0x4b5360':{'0x4b53b0':'initialized heap contract'},'0x4de3e0':{'0x4de3fb':'initialized heap contract'},'0x4c6270':{a:'valid lookup table:588190 never returns true with a null iteration node' for a in ['0x4c62a4','0x4c62a6']}}
for a,c in coverage.items():c['excluded']=excluded.get(a,{});assert set(c['missing'])==set(c['excluded']),(a,c)
training=read(p/'training-scene-finalize-original.json');old_training=read(p/'training-mesh-register-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x409cb0'
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
for k in ['io_calls','gpu_calls','index_calls','crt_calls']:assert training[k]==old_training[k]
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x409cb0')
state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k not in ['mesh','scene','model_object']}=={k:v for k,v in old_state.items() if k not in ['mesh','scene']}
mesh=state['mesh'];scene=state['scene'];model=state['model_object']
assert all(mesh[k]==v for k,v in old_state['mesh'].items() if k!='list_node') and mesh['list_node'] is None
assert all(scene[k]==v for k,v in old_state['scene'].items() if k!='mesh_head') and scene['mesh_head']=='0x0'
assert model['scene']==scene['scene'] and model['dictionary']==state['texture_asset']['dictionary'] and model['methods']=='0x64a490'
assert b['asset_continuation']=={'model':model['object'],'instruction':'0x409cb0'}
for fn in ['0x49c910','0x4c6270','0x4b5360','0x4b5e50','0x4b5e90','0x4dddf0','0x4dde20','0x4de3e0','0x4ddfa0','0x490a60','0x4b7b30','0x4b7ed0','0x4d3ce0']:assert b['native_entries'][fn]==1
assert b['native_entries']['0x4b44d0']==2
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-scene-finalize-fixtures.json');annotated=[]
for i,c in enumerate(fixture['cases']):
 for j,step in enumerate(c['steps']):
  if 'global_bit_masks' in step:
   actual={}
   for index,mask in step['global_bit_masks'].items():
    name,address,width,offset=fixture['globals'][int(index)]
    assert name=='thug_asset_options_storage_draft' and address==0x691758+offset and width==4;actual[offset]=mask
   assert actual=={0:255,12:0,16:65535,56:255,60:0,64:0,68:0,72:0} and step['expected_trap'];annotated.append((i,j))
assert annotated==[(1,10)]
arena=bytearray((p/fixture['memory']).read_bytes());base=fixture['base'];case=fixture['cases'][1]
for address,data in case.get('patches',[]):arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
for step in case['steps']:
 for address,data in step['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
word=lambda a:int.from_bytes(arena[a-base:a-base+4],'little')
model_bytes=(asset_dir/'Letter_S.mdl.xbx').read_bytes()
for key in ['cpu_vertices','gpu_vertices']:
 at=int(mesh[key],16);assert arena[at-base:at-base+3888]==model_bytes[798:4686]
mesh_at=int(mesh['mesh'],16);geometry=int(scene['geometry'],16);scene_at=int(scene['scene'],16);header=int(state['materials']['scene_header'],16);model_at=int(model['object'],16)
assert word(geometry+0x38)==0 and word(geometry+0x40)==1
assert word(geometry+0x3c)==int(mesh['mesh_array'],16) and word(word(geometry+0x3c))==mesh_at
assert word(header+0x1c)==int(scene['render_array'],16) and word(word(header+0x1c))==mesh_at
assert [word(header+o) for o in [0x20,0x24,0x28,0x2c,0x30,0x34]]==[1,0,1,1,1,0]
assert word(model_at)==0x64a490 and word(model_at+4)==int(model['dictionary'],16) and word(model_at+0xc4)==scene_at
assert word(model_at+0xb4)==word(header+0x74)==0 and word(model_at+0xb8)==word(header+0x78)==0
key=word(int(state['model_asset']['asset'],16)+4);signed_key=key if key<0x80000000 else key-0x100000000
assert scene['name']==str(signed_key)+'\n' and hex(word(scene_at+0x84))==scene['name_crc']
context=0x1000020;events=[tuple(word(word(context+12)+i*48+j*4) for j in range(4)) for i in range(word(context+8))]
releases=[e[1] for e in events if e[0]==2];assert releases[-2:]==[0x22bfa08,0x22bf7dc]
unit=read(p/'scene-finalize-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==18
assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Eighteen routines recover mesh-list unlink/delete, shared vertex binding, geometry finalization, '
 'scene mesh count/fill/allocation, the original mesh comparator and sorting/classification, scene '
 'naming/finalization, model construction/binding and render-cache reset.311 cases613 direct calls '
 'cover551/555 instructions; two heap-bootstrap calls are outside the initialized-heap contract '
 'and two instructions cannot occur with a valid588190 iterator. Existing original CRTqsort is '
 'reused, including tie ordering. All new comparisons have zero NaN allowances. Two training '
 'cases22 calls include one interruption. Node204 completes; node1289 finalizes its loaded '
 'scene, converts and releases the temporary mesh list, prepares and sorts its render array, '
 'constructs a model object and binds the scene and texture dictionary. Original4b3ad0 and '
 '48c030 return;409cb0 is the next asset-parser continuation. Full model/mesh loading remains '
 'partial for companion, compressed, transform and effect paths. Actual Chromium passes52 '
 'suites and all50 inherited summaries are identical. Only the same28 proven uninitialized '
 'option bytes are masked. Host GPU/CRT are comparison providers; main build unchanged. '
 'Asset finalization, actual rendering and playable gameplay remain unfinished.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all52 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['scene-finalize-draft.c','scene-finalize-register-derived.c','scene-finalize-scene-derived.c','scene-finalize-material-derived.c',
 'build-scene-finalize-draft.py','scene-finalize-draft.wasm','scene-finalize-draft.build.json','scene-finalize-instructions.txt','scene-finalize-inspection.txt','scene-finalize-tail-inspection.txt',
 'probe-scene-finalize.py','scene-finalize-fixtures.json','scene-finalize-memory.bin','scene-finalize-original.json','scene-finalize-probe.log',
 'scene-finalize-ports.c','scene-finalize-ports.wasm','scene-finalize-ports.build.json',
 'probe-training-scene-finalize.py','training-scene-finalize-fixtures.json','training-scene-finalize-memory.bin','training-scene-finalize-original.json','training-scene-finalize-probe.log',
 'training-scene-finalize-boundary.c','training-scene-finalize-boundary.wasm','training-scene-finalize-boundary.build.json',
 'verify-scene-finalize-checkpoint.mjs','scene-finalize-full-node.log','scene-finalize-browser.html','scene-finalize-worker.mjs','serve-scene-finalize.py',
 'scene-finalize-browser.json','pin-scene-finalize.py','audit-scene-finalize.py','scene-finalize-ghidra.log']
files += ['scene-finalize-checkpoint-'+n+'-result.json' for n in names]
files += [str(f.relative_to(p)) for f in sorted((p/'scene-finalize-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='scene-finalize-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/mesh-register-checkpoint.json','local/analysis/mesh-register-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':18,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':293,'unpromoted_functions_across_separate_experiments':310,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':52,'new_cases':313,'new_calls_including_existing_dependencies':635,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
