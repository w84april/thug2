"""Freeze original/Node/Chromium scene registration evidence without changing prior pins."""
import hashlib,json,struct,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'geometry-clone-checkpoint.json';proof_path=p/'geometry-clone-browser.json';assert not target.exists() and not proof_path.exists()
prior_path=p/'level-register-checkpoint.json';assert sha(prior_path)=='4872b15315cf44fbee0adcf6a959f5afb4043a2b59bdfd4c79b3fcc73dbcc991';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'geometry-clone-draft.build.json');module=p/'geometry-clone-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='04a6fb7fe25a376ca8a15512c85b9fb5e0f7f5aeec22c2c7eb92ef08bd2828e3' and module.stat().st_size==604015
previous=read(p/'level-register-browser.json')['suites'];names=['geometry-clone','training-geometry-clone','training-geometry-clone-shared']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('geometry-clone-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==74
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
for name,expected in [('geometry_clone',(209,285,10,0)),('training_geometry_clone',(1,194,5,0)),('training_geometry_clone_shared',(1,194,5,0))]:
 s=suites[name];assert (s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'geometry-clone-original.json');assert (unit['cases'],unit['calls'])==(209,285)
c=unit['instruction_coverage']['0x4b4510'];assert (c['covered'],c['total'])==(67,69) and set(c['missing'])==set(c['excluded'])=={'0x4b4533','0x4b4567'}
assert unit['instruction_coverage']['0x41ffa0']=={'total':30,'covered':30,'missing':[]}
assets=r/'local/game-files/Game/Data/levels/TR';tex=(assets/'TR.tex.xbx').read_bytes();scn=(assets/'TR.scn.xbx').read_bytes();training=[]
assert len(tex)==3915744 and len(scn)==2770439
assert sha(assets/'TR.tex.xbx')=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(assets/'TR.scn.xbx')=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
for shared in [False,True]:
 name='training-geometry-clone'+('-shared' if shared else '');t=read(p/(name+'-original.json'));training.append(t)
 assert (t['cases'],t['calls'],t['textures'],t['materials'],len(t['sectors']),len(t['meshes']),len(t['billboards']),t['material_groups'])==(1,194,596,870,790,2269,56,7)
 assert t['shared']==shared and t['buffer_calls']==([2350,2406,2406] if shared else [4538,4594,4594])
 assert t['crt_calls']==13614 and t['heap_events']==50854 and t['file_calls']=={'1':104652,'2':542} and t['gpu_calls']=={'1':596,'2':2486,'3':2486}
 assert t['file_position']==len(scn) and t['scene_sha256']==sha(assets/'TR.scn.xbx') and t['texture_sha256']==sha(assets/'TR.tex.xbx')
 assert t['instruction_coverage']['0x48ccb0']=={'covered':63,'total':63,'missing':[]}
 fixture=read(p/(name+'-fixtures.json'));base=fixture['base'];arena=bytearray((p/fixture['memory']).read_bytes());assert base==0x800000 and len(arena)==0x2600000
 assert arena[0x100000:0x100000+len(tex)]==tex and arena[0x500000:0x500000+len(scn)]==scn
 assert fixture['float_fields']==[] and fixture['indirect_globals']==['thug_mesh_material_table'];assert len(fixture['cases'])==1
 case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==194
 assert [s['fn'] for s in case['steps']]==['0x49f050','0x48ccb0']+['0x48c510']*18+['0x420bf0','0x41ffa0']*87
 for s in case['steps']:
  assert not s.get('expected_trap') and 'global_bit_masks' not in s and not s.get('float_fields') and not s.get('quiet_float_fields')
  for address,data in s['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
 w=lambda a:struct.unpack_from('<I',arena,a-base)[0];raw=lambda a,n:arena[a-base:a-base+n];f=lambda a:struct.unpack_from('<f',arena,a-base)[0]
 assert w(base+0x2000)==base+0x500000+len(scn) and w(base+0x1100)==105194
 assert [w(base+0x1200+o) for o in [8,12,16,20,24,28,32]]==[13614,*t['buffer_calls'],1,1,t['add_refs']]
 assert w(base+0x208)==50854 and w(base+0x1004)==596 and w(base+0x1008)==5568
 scene=t['scene'];header=t['header'];assert w(scene+0x280)==header and w(w(scene+0xd0)+8)==790 and w(w(header+0x18)+8)==870
 filename=b'levels\\TR\\TR.scn.Xbx\0';assert raw(scene+4,len(filename))==filename
 assert w(scene+0x88)==case['steps'][0]['result'] and w(header+0x20)==w(header+0x28)==2269
 assert list(struct.unpack('<12I',raw(header+0x44,48)))==t['bounds']
 registry=t['registry'];assert registry[0:3]==[0x648a3c,0xffffffff,0] and registry[3]==registry[4]
 node=registry[3];assert list(struct.unpack('<5I',raw(node,20)))==[0x648a38,scene,0,0x6fa7e0,0x6fa7e0]
 recorded=case['steps'][-1]['globals'];gi=next(i for i,g in enumerate(fixture['globals']) if g[0]=='thug_level_scene_sentinel_draft')
 assert recorded[gi:gi+5]==registry and recorded[gi+5]==node
 seen=[];mesh_by_ptr={m['mesh']:m for m in t['meshes']}
 for sector in t['sectors']:
  g=sector['geometry'];assert w(sector['sector']+4)==sector['key'] and w(sector['sector']+0x14)==g and w(g+0x34)==scene
  assert w(g+0x38)==0 and w(g+0x40)==len(sector['meshes'])
  assert [w(w(g+0x3c)+i*4) for i in range(w(g+0x40))]==sector['meshes'];seen+=sector['meshes']
 assert len(seen)==2269 and set(seen)==set(mesh_by_ptr)
 ordered=[w(w(header+0x1c)+i*4) for i in range(2269)];assert ordered==t['sorted_meshes'] and set(ordered)==set(seen)
 # Independently check monotonic sort keys and render-pass ranges for actual data.
 def sort_key(mesh):
  mat=w(mesh+0x14);return(f(mat+0x1c),raw(mat+12,1)[0],bool(w(mat+0x20)&0x10),w(mesh+0x44),mat)
 assert all(sort_key(a)<=sort_key(b) for a,b in zip(ordered,ordered[1:]))
 alpha=[i for i,m in enumerate(ordered) if w(w(m+0x14)+0x20)&0x40];special=[i for i in alpha if raw(w(ordered[i]+0x14)+12,1)[0]]
 assert [w(header+o) for o in [0x24,0x2c,0x30,0x34]]==[len(alpha),min(alpha,default=2269),min(special,default=2269),len(special)]
 assert sum(m['vertices'] for m in t['meshes'])==50814 and sum(sum(m['index_counts']) for m in t['meshes'])==77029
 billboards={b['mesh']:b['record'] for b in t['billboards']};shared_device,shared_bytes=t['shared_buffer'];assert [w(header+o) for o in [0x7c,0x80]]==[shared_device,shared_bytes]
 shared_ranges=[]
 for at,m in mesh_by_ptr.items():
  assert w(at)==m['flags'] and w(at+0x14)==m['material'] and w(m['material'])==m['key'] and w(at+0xcc)==m['vertex_buffer']
  v=m['vertex_buffer'];n=w(v);gpu=w(v+8);offset=w(v+32)
  assert struct.unpack('<H',raw(at+0x22,2))[0]==m['vertices'] and raw(at+0x18,1)[0]==m['stride']
  if at not in billboards:assert raw(w(v+12),n)==raw(gpu+256+offset,n)
  else:assert list(struct.unpack('<9I',raw(w(at+0x4c),36)))==billboards[at]
  if shared and gpu==shared_device:shared_ranges.append((offset,(n+31)&~31))
  for slot,count in enumerate(m['index_counts']):
   if count:
    v=w(at+0x54+slot*4);assert raw(w(v+16),count*2)==raw(w(v+12)+256,count*2)
 if shared:
  assert shared_bytes==1941440 and len(shared_ranges)==t['add_refs']==w(shared_device+16)==2189
  cursor=0
  for offset,n in sorted(shared_ranges):assert offset==cursor;cursor+=n
  assert cursor==shared_bytes
 else:assert shared_device==shared_bytes==t['add_refs']==0
 sector_map={s['key']:s['sector'] for s in t['sectors']};assert len(t['lookups'])==18
 for key,value in t['lookups']:assert value==sector_map.get(key,0)
 # Validate every real LevelObject model, its private geometry/header/instance,
 # and buffer sharing independently of the original probe's assertions.
 inventory=read(p/'training-scene-node-inventory.json')['nodes'];selected=[n for n in inventory if n['class_text']=='LevelObject']
 assert len(t['objects'])==len(selected)==87 and sum(o['bound'] for o in t['objects'])==85 and t['cloned_meshes']==173
 assert sum(n['created_at_start'] for n in selected)==31
 clones=[];instances=[];source_by_key={s['key']:s for s in t['sectors']}
 for o,n in zip(t['objects'],selected):
  assert all(o[k]==v for k,v in n.items());component=o['component'];renderer=o['renderer'];head=w(renderer+0x10);node=w(head+4)
  assert w(component)==0x646128 and w(component+0x208)==renderer and raw(component+0x235,1)[0]==o['bound'] and w(renderer)==0x64a4b4
  source=source_by_key.get(int(o['name'],16));assert bool(source)==bool(o['bound'])
  if not source:assert node==head and w(head+8)==head and w(renderer+0x14)==0;continue
  part=w(node);geometry=o['geometry'];instance=o['instance'];private=o['private_header'];count=len(o['cloned_meshes']);original_geometry=source['geometry']
  assert w(node+4)==w(node+8)==head and w(head+8)==node and w(renderer+0x14)==1
  assert struct.unpack('<H',raw(renderer+0x46,2))[0]==1 and w(renderer+4)==0 and w(renderer+0x30)==0x9facc1a5
  assert list(struct.unpack('<6I',raw(part,24)))==[geometry,0,0,0,0,0]
  assert [w(geometry+i*4) for i in range(4)]==[0x64a368,1,w(original_geometry+8),0]
  assert w(geometry+0x38)==0 and w(geometry+0x40)==count and w(geometry+0x4c)==instance
  assert raw(geometry+0x14,32)==raw(original_geometry+0x14,32)
  assert [w(w(geometry+0x3c)+i*4) for i in range(count)]==o['cloned_meshes']
  for a,b in zip(source['meshes'],o['cloned_meshes']):
   assert a!=b and w(b)==w(a)|0x41
   # Actual training LevelObject meshes have no auxiliary arrays requiring copies.
   assert w(a+0xac)==0 and raw(a+4,212)==raw(b+4,212)
  private_order=[w(w(private+0x1c)+i*4) for i in range(count)]
  assert w(private+0x20)==w(private+0x28)==count and set(private_order)==set(o['cloned_meshes'])
  assert all(sort_key(a)<=sort_key(b) for a,b in zip(private_order,private_order[1:]))
  assert raw(private+0x44,32)==raw(geometry+0x14,32) and w(instance+0x58)==private
  identity=[0x3f800000 if i%5==0 else 0 for i in range(16)]
  assert list(struct.unpack('<16I',raw(instance+4,64)))==identity and w(instance+0x44)==0 and w(instance+0x48)==1
  assert raw(instance+0x4c,1)[0]==1 and w(instance+0x54)==0 and w(instance+0x60)==0xffffffff
  eligible=all(w(m+0x38)&0x10 and not(w(m)&0x20000) for m in private_order)
  assert w(instance)==1|(2 if eligible else 0)
  assert w(instance+0x5c)==(instances[-1] if instances else 0)
  clones+=o['cloned_meshes'];instances.append(instance)
 assert len(clones)==len(set(clones))==173 and len(instances)==85
 ri=next(i for i,g in enumerate(fixture['globals']) if g[0]=='thug_model_render_instances_draft');assert recorded[ri]==instances[-1]
 port=read(p/(name+'-ports.build.json'));assert sha(p/'training-level-register-ports.c')==port['source_sha256'] and sha(p/(name+'-ports.wasm'))==port['sha256']
 assert t['specimen_sha256']==unit['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Recovered private geometry render-list construction4b4510 and LevelObject model binding41ffa0. Shared mesh/geometry cloning4d71f0/4b58c0, virtual clone wrapper48dd80 and mandatory renderer append4938e0 support the original LevelObject path; deep-copy, scene-merge and optional allocation remain explicit traps.209 unit cases285calls include actual420d10 class/name/scale selection and bounds-cache tail. After loading untouched training assets, both vertex-buffer modes bind all87 actual LevelObject names through real Model constructors:85 render instances173 shared-buffer mesh clones, two missing-geometry no-ops.31 startup LevelObject names are included; this does not yet dispatch their original node creation scripts or other components. Entire arenas, original CRT operations, globals and GPU comparison storage agree without masks/NaN allowances.74 Node/Chromium suites pass;71 inherited summaries unchanged. Main unchanged; drawing and playable gameplay remain incomplete.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all74 summaries and complete DOM fingerprint inspected','browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files={f for f in (p/'geometry-clone-ghidra').rglob('*') if f.is_file()}
for pattern in ['geometry-clone-*','training-geometry-clone-*','*geometry-clone*.py','verify-geometry-clone-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'geometry-clone-audit.json',p/'geometry-clone-next.txt'})
assert p/'audit-geometry-clone.py' in files and p/'pin-geometry-clone.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/level-register-checkpoint.json','local/analysis/level-register-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':2,'original_addresses':['0x4b4510','0x41ffa0'],'partial_original_addresses':['0x4d71f0','0x4b58c0','0x48dd80','0x4938e0','0x420d10'],'unpromoted_functions_in_this_module':326,'unpromoted_functions_across_separate_experiments':343,'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':74,'new_cases':211,'new_calls_including_existing_dependencies':673,'new_interrupted_calls':0,'actual_training':[{k:v if k not in ['sectors','meshes','billboards','buffers','sorted_meshes','objects'] else len(v) for k,v in t.items() if k!='scope'} for t in training],'instruction_coverage':unit['instruction_coverage'],'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n');print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
