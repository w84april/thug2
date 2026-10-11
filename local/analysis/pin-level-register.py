"""Freeze original/Node/Chromium scene registration evidence without changing prior pins."""
import hashlib,json,struct,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
target=p/'level-register-checkpoint.json';proof_path=p/'level-register-browser.json';assert not target.exists() and not proof_path.exists()
prior_path=p/'level-sector-checkpoint.json';assert sha(prior_path)=='e2e0d3978580c33cce7d28b924dc916d2fbe69713eeada8b482599c0b94f93be';prior=read(prior_path)
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in prior[group].items():assert sha(r/name)==digest,(group,name)
build=read(p/'level-register-draft.build.json');module=p/'level-register-draft.wasm';assert build['source_hashes']==prior['source_hashes']
for name,digest in {**build['source_hashes'],**build['draft_source_hashes'],**build['derived_from']}.items():assert sha(r/name)==digest,name
assert sha(module)==build['sha256']=='e916e239be0ace851cb6e1caf42724f4e217325a54bac87947b05b90a47de275' and module.stat().st_size==601632
previous=read(p/'level-sector-browser.json')['suites'];names=['level-register','training-level-register','training-level-register-shared']+[n.replace('_','-') for n in previous]
suites={n.replace('-','_'):read(p/('level-register-checkpoint-'+n+'-result.json')) for n in names};assert len(suites)==71
for name,suite in suites.items():
 assert suite['result']=='pass',name
 if name in previous:assert suite==previous[name],name
for name,expected in [('level_register',(69,339,2,0)),('training_level_register',(1,20,3,0)),('training_level_register_shared',(1,20,3,0))]:
 s=suites[name];assert (s['cases'],s['calls'],s['functions'],s['nan_fields_classification_only'])==expected
candidate={'result':'pass','wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'runtime_imports':0,'suites':suites}
canonical=json.dumps(candidate,sort_keys=True,ensure_ascii=False,separators=(',',':'));h=14695981039346656037
for char in canonical:h=((h^ord(char))*1099511628211)&((1<<64)-1)
assert sys.argv[1]==f'{h:016x}' and int(sys.argv[2])==len(canonical) and int(sys.argv[3])==len(candidate)==5
unit=read(p/'level-register-original.json');assert (unit['cases'],unit['calls'])==(69,339)
c=unit['instruction_coverage']['0x48c560'];assert (c['covered'],c['total'])==(55,56) and set(c['missing'])==set(c['excluded'])=={'0x48c608'}
assets=r/'local/game-files/Game/Data/levels/TR';tex=(assets/'TR.tex.xbx').read_bytes();scn=(assets/'TR.scn.xbx').read_bytes();training=[]
assert len(tex)==3915744 and len(scn)==2770439
assert sha(assets/'TR.tex.xbx')=='13c28cf820dd4bb989579915ab533b7651ea178ef664d44ad9ec1fc754fa6d21'
assert sha(assets/'TR.scn.xbx')=='a4e185b0f050e181850c341a3378b54f1b37adce3099d3568600bf2e02e61332'
for shared in [False,True]:
 name='training-level-register'+('-shared' if shared else '');t=read(p/(name+'-original.json'));training.append(t)
 assert (t['cases'],t['calls'],t['textures'],t['materials'],len(t['sectors']),len(t['meshes']),len(t['billboards']),t['material_groups'])==(1,20,596,870,790,2269,56,7)
 assert t['shared']==shared and t['buffer_calls']==([2350,2406,2406] if shared else [4538,4594,4594])
 assert t['crt_calls']==13614 and t['heap_events']==49912 and t['file_calls']=={'1':104652,'2':542} and t['gpu_calls']=={'1':596,'2':2486,'3':2486}
 assert t['file_position']==len(scn) and t['scene_sha256']==sha(assets/'TR.scn.xbx') and t['texture_sha256']==sha(assets/'TR.tex.xbx')
 assert t['instruction_coverage']['0x48ccb0']=={'covered':63,'total':63,'missing':[]}
 fixture=read(p/(name+'-fixtures.json'));base=fixture['base'];arena=bytearray((p/fixture['memory']).read_bytes());assert base==0x800000 and len(arena)==0x2600000
 assert arena[0x100000:0x100000+len(tex)]==tex and arena[0x500000:0x500000+len(scn)]==scn
 assert fixture['float_fields']==[] and fixture['indirect_globals']==['thug_mesh_material_table'];assert len(fixture['cases'])==1
 case=fixture['cases'][0];assert not case['patches'] and len(case['steps'])==20
 assert [s['fn'] for s in case['steps']]==['0x49f050','0x48ccb0']+['0x48c510']*18
 for s in case['steps']:
  assert not s.get('expected_trap') and 'global_bit_masks' not in s and not s.get('float_fields') and not s.get('quiet_float_fields')
  for address,data in s['outputs']:arena[address-base:address-base+len(data)//2]=bytes.fromhex(data)
 w=lambda a:struct.unpack_from('<I',arena,a-base)[0];raw=lambda a,n:arena[a-base:a-base+n];f=lambda a:struct.unpack_from('<f',arena,a-base)[0]
 assert w(base+0x2000)==base+0x500000+len(scn) and w(base+0x1100)==105194
 assert [w(base+0x1200+o) for o in [8,12,16,20,24,28,32]]==[13614,*t['buffer_calls'],1,1,t['add_refs']]
 assert w(base+0x208)==49912 and w(base+0x1004)==596 and w(base+0x1008)==5568
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
 def key(mesh):
  mat=w(mesh+0x14);return(f(mat+0x1c),raw(mat+12,1)[0],bool(w(mat+0x20)&0x10),w(mesh+0x44),mat)
 assert all(key(a)<=key(b) for a,b in zip(ordered,ordered[1:]))
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
 port=read(p/(name+'-ports.build.json'));assert sha(p/'training-level-register-ports.c')==port['source_sha256'] and sha(p/(name+'-ports.wasm'))==port['sha256']
 assert t['specimen_sha256']==unit['specimen_sha256']==prior['specimen_sha256']
assert sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
scope=('Recovered scene registration48c560 under initialized registry, fitting128-byte path and successful allocation contracts;69 cases339 calls, with only the allocation-failure instruction excluded. Partial wrapper48ccb0 now performs original full training scene loading, finalization and registration with shared vertices disabled/enabled. Both actual file paths match every arena/global byte without masks or NaN allowances:790 sectors2269 sorted meshes,18 lookup checks each; shared mode binds2189 meshes into1941440 bytes. All71 Node/Chromium suites pass,68 inherited summaries unchanged. Loader material layers and optional tail records still trap. Registry destruction, script scene-loading binding, production drawing and gameplay remain unfinished. Main unchanged; not playable.')
proof={**candidate,'recorded_at':sys.argv[4],'observed_via':'Actual Chromium PASS at '+sys.argv[5]+'; all71 summaries and complete DOM fingerprint inspected','browser_dom_fingerprint':{'algorithm':'FNV-1a-64 over canonical sorted JSON characters','value':sys.argv[1],'characters':len(canonical)},'scope':scope}
proof_path.write_text(json.dumps(proof,indent=2)+'\n')
files=set()
for pattern in ['level-register-*','training-level-register-*','*level-register*.py','verify-level-register-checkpoint.mjs']:
 files.update(f for f in p.glob(pattern) if f.is_file() and f not in {target,p/'level-register-audit.json',p/'level-register-next.txt'})
assert p/'audit-level-register.py' in files and p/'pin-level-register.py' in files
artifacts=set(prior['artifact_hashes'])|{'local/analysis/level-sector-checkpoint.json','local/analysis/level-sector-audit.json'}|{str(f.relative_to(r)) for f in files}
pin={'result':'original, Node and actual Chromium comparisons pass; unpromoted','new_functions':1,'original_addresses':['0x48c560'],'partial_original_addresses':['0x48ccb0'],'unpromoted_functions_in_this_module':324,'unpromoted_functions_across_separate_experiments':341,'specimen_sha256':unit['specimen_sha256'],'wasm_sha256':sha(module),'wasm_bytes':module.stat().st_size,'main_wasm_sha256':prior['main_wasm_sha256'],'browser_suites':71,'new_cases':71,'new_calls_including_existing_dependencies':379,'new_interrupted_calls':0,'actual_training':[{k:v if k not in ['sectors','meshes','billboards','buffers','sorted_meshes'] else len(v) for k,v in t.items() if k!='scope'} for t in training],'instruction_coverage':unit['instruction_coverage'],'source_hashes':build['source_hashes'],'artifact_hashes':{n:sha(r/n) for n in sorted(artifacts)},'harness_hashes':prior['harness_hashes'],'checker_dependency_hashes':prior['checker_dependency_hashes'],'browser_dom_fingerprint':proof['browser_dom_fingerprint'],'scope':scope}
target.write_text(json.dumps(pin,indent=2)+'\n');print(json.dumps({'result':'pinned','artifacts':len(pin['artifact_hashes']),'sources':len(pin['source_hashes']),'checkpoint_sha256':sha(target),'main_unchanged':True}))
