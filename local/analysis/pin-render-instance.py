"""Freeze original, Node and actual Chromium renderer attachment comparisons."""
import hashlib,json,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'render-instance-checkpoint.json';proof_path=p/'render-instance-browser.json'
assert not target.exists() and not proof_path.exists()
prior_path=p/'asset-ready-checkpoint.json';assert sha(prior_path)=='574aef43bb95348a89a51e1120e01f089bc982e067b12f0f0b68cfffd3c1c360'
prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'render-instance-draft.build.json');module=p/'render-instance-draft.wasm'
assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='e142e61919b8ef2b4da50955a2f006152c84bb58198f8a65a2d9f981600004f8'
assert module.stat().st_size==581904
meta=read(p/'training-render-instance-boundary.build.json')
assert sha(p/'training-render-instance-boundary.c')==meta['source_sha256'] and sha(p/'training-render-instance-boundary.wasm')==meta['sha256']
previous=read(p/'asset-ready-browser.json')['suites'];names=['render-instance','training-render-instance']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('render-instance-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==56
for n,s in suites.items():
 assert s['result']=='pass',n
 if n in previous:assert s==previous[n],n
s=suites['render_instance'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(170,248,6,0)
s=suites['training_render_instance'];assert(s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==(2,22,8,0)
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
original=read(p/'render-instance-original.json');coverage=original['instruction_coverage']
assert(original['cases'],original['calls'])==(170,248) and len(coverage)==6
assert sum(t['covered'] for t in coverage.values())==150 and sum(t['total'] for t in coverage.values())==161
for a,c in coverage.items():
 c['excluded']=({'0x4b5567':'initialized heap contract'} if a=='0x4b54b0' else {'0x4964ac':'initialized heap contract',**{x:'successful allocation contract; original NULL dereference' for x in ['0x4964ed','0x4964f0','0x4964f2','0x4964f3','0x4964f6','0x4964f9','0x4964fc','0x4964ff','0x496500']}} if a=='0x4964a0' else {})
 assert set(c['missing'])==set(c['excluded']),(a,c)
training=read(p/'training-render-instance-original.json');old_training=read(p/'training-asset-ready-original.json')
assert(training['cases'],training['calls'])==(2,22)
for part in ['partial_model_load','partial_configuration','partial_geometry_load','partial_mesh_buffer','partial_sector_parser']:
 assert training[part]['complete'] is False and training[part]['boundary']=='0x421191'
 assert set(old_training[part]['executed'])<=set(training[part]['executed'])
for k in ['io_calls','gpu_calls','index_calls','crt_calls']:assert training[k]==old_training[k]
a,b=training['nodes'];assert(a['node_index'],a['completed_calls'],a['interrupted_calls'],a['execute_result'])==(204,11,0,0)
assert(b['node_index'],b['completed_calls'],b['interrupted_calls'],b['first_missing_routine'])==(1289,10,1,'0x421191')
state=b['model_state'];old_state=old_training['nodes'][1]['model_state']
assert {k:v for k,v in state.items() if k!='render_instance'}==old_state
asset=state['model_asset'];model=state['model_object'];mesh=state['mesh'];scene=state['scene'];render=state['render_instance']
assert b['asset_continuation']=={'component':state['component'],'instruction':'0x421191','renderer':state['renderer'],'parameters':'0x22bd4c8'}
for fn in ['0x4d1030','0x4b54b0','0x492e50','0x48ddf0','0x49f3b0','0x4964a0']:assert b['native_entries'][fn]==1
assert training['partial_model_load']['covered_instructions']==177 and old_training['partial_model_load']['covered_instructions']==101
asset_dir=r/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S'
assert sha(asset_dir/'Letter_S.mdl.xbx')==training['model_file_sha256']==old_training['model_file_sha256']
assert sha(asset_dir/'Letter_S.tex.xbx')==training['texture_file_sha256']==old_training['texture_file_sha256']
fixture=read(p/'training-render-instance-fixtures.json');annotated=[]
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
at=int(asset['asset'],16);texture=int(state['texture_asset']['asset'],16);model_at=int(model['object'],16)
assert word(at+8)==4 and word(at+0x10)==model_at and word(at+0x24)==int(asset['buffer'],16)
assert all(word(at+o)==0 for o in [0x20,0x50,0x54,0x58,0x5c])
assert word(model_at)==0x64a490 and word(model_at+4)==int(model['dictionary'],16) and word(model_at+0xc4)==int(scene['scene'],16)
manager=0x10f0000;table=word(manager+0x1c);assert word(table+8)==2 and word(manager+0x20)==texture
buckets=word(table+4);values={word(buckets+i*12+4) for i in range(1<<word(table)) if word(buckets+i*12+4)}
assert values=={at,texture}
assert [word(at+0x2c),word(at+0x30),word(texture+0x2c),word(texture+0x30)]==[texture,texture,at,at]
mask_index=next(i for i,g in enumerate(fixture['globals']) if g[0]=='thug_asset_options_mask_draft');assert case['steps'][-1]['globals'][mask_index]==0
assert [word(0x100e000+i*4) for i in range(6)]==[0x421191,int(state['component'],16),int(state['renderer'],16),1,0x22bd4c8,0]
renderer=int(state['renderer'],16);geometry=int(render['geometry'],16);instance=int(render['instance'],16);part=int(render['part'],16);node=int(render['list_node'],16);head=int(state['sentinel'],16);header=int(render['scene_header'],16)
assert [word(part+i*4) for i in range(6)]==[geometry,int(model['dictionary'],16),0,0,word(at+4),0]
assert word(geometry)==0x64a368 and word(geometry+4)==1 and word(geometry+0x4c)==instance and word(geometry+0x50)==model_at
assert [word(instance+4+i*4) for i in range(16)]==[0x3f800000 if i%5==0 else 0 for i in range(16)]
assert [word(instance+o) for o in [0,0x44,0x48,0x54,0x58,0x5c,0x60]]==[0,0,0,renderer,header,0,0xffffffff]
assert arena[instance+0x4c-base]==1
assert [word(renderer+o) for o in [4,0x14,0x18,0x30]]==[0,1,1,word(at+4)]
assert [int.from_bytes(arena[renderer+o-base:renderer+o-base+2],'little') for o in [0x46,0x48,0x4a]]==[1,0,1]
assert [word(node+i*4) for i in range(3)]==[part,head,head] and word(head+4)==node and word(head+8)==node
registry_index=next(i for i,g in enumerate(fixture['globals']) if g[0]=='thug_model_render_instances_draft');assert case['steps'][-1]['globals'][registry_index]==instance
unit=read(p/'render-instance-fixtures.json');assert unit['float_fields']==[] and len(unit['functions'])==6
assert 'pointer_initializers' not in unit and 'native_callbacks' not in unit
assert all('global_bit_masks' not in s for c in unit['cases'] for s in c['steps'])
assert original['specimen_sha256']==training['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=(
 'Six routines recover render-instance construction, geometry model binding and its PC implementation, '
 'renderer skeleton access, the actual flag virtual and renderer part-list insertion.170 cases248 calls '
 'compare150/161 original instructions; exclusions are two initialized-heap calls and nine instructions '
 'on a failing allocation branch that dereferences NULL. Raw matrix bits including NaNs and forward '
 'overlap compare exactly. The original model-loading asset branch now creates a render instance, '
 'links the global registry, binds the model scene, fills its part and inserts it into the renderer. '
 'Two training cases22 calls include one interruption: node204 completes; node1289 reaches421191 '
 'after4935e0 returns, before the configuration tail. All prior scene/model/mesh/asset state and '
 'GPU/CRT/I/O counts are preserved. New comparisons have zero NaN allowances and only the same28 '
 'proven option padding bytes are masked. Chromium passes56 suites with all54 inherited summaries '
 'unchanged. The main build is unchanged. General loading routes, configuration bounds, rendering '
 'and playable gameplay remain incomplete.'
)
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all56 summaries and complete DOM fingerprint inspected',
 'browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
files=['render-instance-draft.c','render-instance-initialize-derived.c','render-instance-load-derived.c','render-instance-configuration-derived.c',
 'build-render-instance-draft.py','render-instance-draft.wasm','render-instance-draft.build.json','render-instance-inspection.txt','render-instance-bounds-inspection.txt','render-instance-bounds-detail-inspection.txt','render-instance-bounds-virtual-inspection.txt','render-instance-bounds-ghidra.log',
 'probe-render-instance.py','render-instance-fixtures.json','render-instance-memory.bin','render-instance-original.json','render-instance-probe.log',
 'probe-training-render-instance.py','training-render-instance-fixtures.json','training-render-instance-memory.bin','training-render-instance-original.json','training-render-instance-probe.log',
 'training-render-instance-boundary.c','training-render-instance-boundary.wasm','training-render-instance-boundary.build.json',
 'verify-render-instance-checkpoint.mjs','render-instance-full-node.log','render-instance-browser.html','render-instance-worker.mjs','serve-render-instance.py',
 'render-instance-browser.json','pin-render-instance.py','audit-render-instance.py']
files += ['render-instance-checkpoint-'+n+'-result.json' for n in names]
files += [str(f.relative_to(p)) for f in sorted((p/'render-instance-bounds-ghidra').rglob('*')) if f.is_file()]
for name in files:
 if name!='render-instance-browser.json':assert(p/name).is_file(),name
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
artifacts=set(prior['artifact_hashes'])|{'local/analysis/asset-ready-checkpoint.json','local/analysis/asset-ready-audit.json'}|{'local/analysis/'+n for n in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':6,'original_addresses':list(coverage),
 'unpromoted_functions_in_this_module':303,'unpromoted_functions_across_separate_experiments':320,
 'specimen_sha256':original['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],
 'browser_suites':56,'new_cases':172,'new_calls_including_existing_dependencies':270,'new_interrupted_calls':1,'actual_training_nodes':training['nodes'],
 'instruction_coverage':coverage,'partial_geometry_load':training['partial_geometry_load'],'partial_sector_parser':training['partial_sector_parser'],'partial_mesh_buffer':training['partial_mesh_buffer'],'indeterminate_option_bytes':state['indeterminate_texture_option_bytes'],
 'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],
 'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n')
print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
