"""Original shared mesh/geometry clones and real LevelObject model binding."""
from pathlib import Path
setup=Path('local/analysis/probe-level-register.py').read_text().split('functions.update(')[0]
exec(compile(setup,'<preserved initialized scene registry fixture>','exec'))
functions.clear();code.clear();hits.clear();labels.clear();oracle.counts.clear()
specs=[(0x4d71f0,907,'mesh_clone',1,'word',True),(0x4b4510,215,'geometry_scene_data',0,'word',True),
 (0x4b58c0,694,'geometry_clone_pc',2,'word',True),(0x48dd80,58,'geometry_clone',2,'word',True),
 (0x4938e0,249,'renderer_append_geometry',3,'byte',True),(0x41ffa0,82,'model_level_object',1,'void',True),
 (0x420bf0,275,'model_component_construct',0,'word',True)]
for a,n,name,argc,result,heap in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
functions['0x48c560']={'name':'thug_level_scene_register_draft','this':False,'result':'void','cleanup':0,'memory':True}
exports += [[0x64a368,'thug_model_geometry_lights_methods_draft'],[0x649348,'thug_model_renderer_base_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft'],[0x646128,'thug_model_component_methods_draft'],[0x648ec8,'thug_model_geometry_base_methods_draft']]
globals_.append(['thug_model_render_instances_draft',0x7825c0,4]);defaults.append(0)
SERVICES,SYMBOLS=BASE+0x16000,BASE+0x1e0000
put(SERVICES,'<3I',0,0,ADAPTER);memory[SYMBOLS-BASE:SYMBOLS-BASE+0x4000]=bytes(0x4000)
globals_ += [['thug_component_services',0x354,4],['thug_script_symbol_buckets',0x6f3624,4]];defaults += [SERVICES,SYMBOLS]
functions['0x420d10']={'name':'thug_model_configuration_prefix_draft','this':True,'result':'void','cleanup':4,'memory':False}
functions['0x4bad90']={'name':'thug_model_renderer_construct_draft','this':True,'result':'word','cleanup':0,'memory':True}
initial=bytes(memory);oracle.initial=initial

def make_mesh(g,i=0,aux=0,triangles=0,fill=0):
 mesh=g.alloc(216);g.data[mesh-BASE:mesh-BASE+216]=bytes([fill])*216
 mat=g.alloc(0x110);g.data[mat-BASE:mat-BASE+0x110]=bytes(0x110);g.put(mat+0x1c,'<f',float(i%5-2));g.put(mat+12,'<B',i%2);g.put(mat+0x20,'<I',0x40 if i%3 else 0)
 g.put(mesh,'<I',0x20000 if i%3 else 0);g.put(mesh+0x14,'<I',mat);g.put(mesh+0x38,'<I',0x10);g.put(mesh+0x44,'<I',i%4)
 g.put(mesh+0xac,'<3I',aux,g.alloc(max(aux,1)*12),triangles);g.put(mesh+0xb8,'<I',g.alloc(max(triangles,1)*6))
 return mesh

def geometry(g,n):
 geo=g.alloc(100);g.data[geo-BASE:geo-BASE+100]=bytes(100);g.put(geo,'<I',0x64a368)
 g.put(geo+0x14,'<8f',-100,-20,-3,1,21,4,15,1);arr=g.alloc(max(n,1)*4);g.put(geo+0x3c,'<2I',arr,n)
 for i in range(n):g.put(arr+i*4,'<I',make_mesh(g,i,aux=i%2,triangles=i%3))
 return geo

for fill in [0,0xa5,0xff]:
 for shared in [1,255,257,0xffffffff]:
  for aux in [0,1,3]:
   for triangles in [0,1,3]:
    g=Graph();mesh=make_mesh(g,2,aux,triangles,fill)
    run(g,[call(0x4d71f0,mesh,[shared])],f'mesh fill{fill}/shared{shared}/aux{aux}/triangles{triangles}')
for n in [0,1,3,9,17]:
 g=Graph();geo=geometry(g,n);run(g,[call(0x4b4510,geo)],f'private scene data/n{n}')
for fn in [0x4b58c0,0x48dd80]:
 for n in [0,1,3,9]:
  for shared in [1,257,0xffffffff]:
   for inherited in [0,P+0x800]:
    g=Graph();geo=geometry(g,n);g.put(geo+8,'<I',inherited)
    run(g,[call(fn,geo,[shared,0])],f'geometry{fn:x}/n{n}/shared{shared}/inherited{inherited:x}')
for count in [0,1,31,32,255,256,65535]:
 for flags in [0,1,0x10,0xff]:
  g=Graph();geo=geometry(g,0);renderer=g.alloc(80);head=g.alloc(12);g.data[renderer-BASE:renderer-BASE+80]=bytes(80)
  g.put(head,'<3I',0,head,head);g.put(renderer,'<2I',0x64a4b4,0 if count%2 else 6);g.put(renderer+0x10,'<2I',head,0)
  g.put(renderer+0x44,'<BBH',flags,0,count);g.put(renderer+0x2c,'<I',P+0x100)
  run(g,[call(0x4938e0,renderer,[geo,P+0x200,257])]*2,f'append count{count}/flags{flags}')
for state in ['missing','no geometry','empty','three meshes']:
 for count in [1,3]:
  g=Graph();scene=g.alloc(644);sector=g.alloc(52);geo=0 if state=='no geometry' else geometry(g,3 if state=='three meshes' else 0)
  g.put(sector+0x14,'<I',geo);table=g.table([] if state=='missing' else [(123,sector)]);g.put(scene+0xd0,'<I',table)
  name=g.alloc(3);g.data[name-BASE:name-BASE+3]=b'TR\0'
  calls=[call(0x48c560,0,[scene,name,0,1,0]),call(0x420bf0,P)]
  calls += [call(0x41ffa0,P,[123])]*count;run(g,calls,f'LevelObject {state}/repeats{count}')
# Reach the newly connected ModelClass branch and its original bounds-cache tail.
for state in ['missing','no geometry','empty','three meshes']:
 for scale in [None,0.5,2.0]:
  g=Graph();g.data[P-BASE:P-BASE+0x238]=bytes(0x238);owner=g.alloc(0x108);g.data[owner-BASE:owner-BASE+0x108]=bytes(0x108)
  renderer=g.alloc(80);g.data[renderer-BASE:renderer-BASE+80]=bytes(80);g.put(P+12,'<I',owner);g.put(P+0x208,'<I',renderer)
  scene=g.alloc(644);sector=g.alloc(52);geo=0 if state=='no geometry' else geometry(g,3 if state=='three meshes' else 0)
  g.put(sector+0x14,'<I',geo);g.put(scene+0xd0,'<I',g.table([] if state=='missing' else [(123,sector)]))
  name=g.alloc(3);g.data[name-BASE:name-BASE+3]=b'TR\0';params=g.alloc(8);items=[(13,0x12b4e660,0xb7b3bd86),(13,0xa1dc81f9,123)]
  if scale is not None:items.append((2,0x13b9da7b,struct.unpack('<I',struct.pack('<f',scale))[0]))
  nodes=[g.alloc(16) for _ in items];g.put(params,'<2I',0,nodes[0])
  for i,((kind,key,value),node) in enumerate(zip(items,nodes)):g.put(node,'<4I',kind*2,key,value,nodes[i+1] if i+1<len(nodes) else 0)
  run(g,[call(0x4bad90,renderer),call(0x48c560,0,[scene,name,0,1,0]),call(0x420d10,P,[params])],f'configuration LevelObject {state}/scale{scale}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
coverage['0x4b4510']['excluded']={'0x4b4533':'initialized allocator contract','0x4b4567':'successful allocation contract'}
assert set(coverage['0x4b4510']['missing'])==set(coverage['0x4b4510']['excluded'])
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
prior=json.loads((folder/'vertex-upload-fixtures.json').read_text())
scope='Original shared-buffer mesh4d71f0 and geometry4b58c0 clones, private render-list/bounds4b4510, virtual wrapper48dd80, mandatory renderer part append4938e0 and actual LevelObject41ffa0 binding plus420d10 class/name/scale selection and bounds-cache tail. Deep-copy/scene-merge and optional allocation paths remain explicit traps. Original constructors, CRT allocations, sort, instance registration, enabled/light virtuals and lookup execute; no rendering supplied. Successful initialized allocator and valid internal graphs required.'
fixture={**prior,'memory':'geometry-clone-memory.bin','globals':globals_,'functions':functions,'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'pointer_globals':registry_pointer_globals,'float_fields':[],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'geometry-clone-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'geometry-clone-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='instruction_coverage'}),flush=True)
