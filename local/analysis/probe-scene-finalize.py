"""Original vertex allocation/upload and shader mapping, with explicit ports."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned heap/GPU setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
CRTCTX,CRTBEGIN,CRTLIMIT,CRTLOG=BASE+0x13000,BASE+0x120000,BASE+0x160000,BASE+0x1d000
INDEXCTL,INDEXLOG,INDEXVT,INDEXDEV=BASE+0x18000,BASE+0x19000,BASE+0x1c000,BASE+0x160000
exec(compile((folder/'vertex-upload-ports-setup.py').read_text(),'<explicit separate CRT and GPU index ports>','exec'))
import random
ADDREF=oracle.stop+0x380;put(INDEXVT+4,'<I',ADDREF)
def add_ref(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);device=oracle.word(sp+4);before=oracle.word(device+4);after=(before+1)&0xffffffff;i=oracle.word(INDEXCTL)
 assert i<128;oracle.setword(INDEXCTL,i+1);oracle.setword(device+4,after);cpu.mem_write(INDEXLOG+i*64,struct.pack('<16I',4,device,before,after,*([0]*12)))
 cpu.reg_write(UC_X86_REG_EAX,after);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+8)
oracle.cpu.hook_add(UC_HOOK_CODE,add_ref,begin=ADDREF,end=ADDREF)
for i in range(6):globals_.append(['thug_model_render_cache_draft',0x7865cc+i*4,4,i*4]);defaults.append(0xabcdef00+i)
initial=bytes(memory);oracle.initial=initial
specs=[(0x4b5ec0,31,'model_mesh_node_unlink',0,'void',False,True),
 (0x4b5e50,58,'model_mesh_node_delete',1,'word',True,True),(0x4b5e90,33,'model_mesh_sentinel_delete',1,'word',True,True),
 (0x4d3e50,115,'mesh_vertex_bind_shared',1,'void',False,True),(0x4b5360,214,'model_geometry_finish_meshes',1,'void',True,True),
 (0x4dddf0,48,'model_scene_count_meshes',2,'void',False,True),(0x4dde20,49,'model_scene_fill_meshes',2,'void',False,True),
 (0x4b44d0,62,'model_geometry_collect_meshes',1,'byte',False,True),(0x4de3e0,54,'model_scene_allocate_meshes',0,'void',True,True),
 (0x4ddd50,156,'model_mesh_compare',0,'word',False,False),(0x4ddfa0,125,'model_scene_sort_meshes',0,'void',False,True),
 (0x4a2ba0,4,'model_sector_geometry',0,'word',False,True),(0x4c6270,334,'model_scene_finalize',1,'void',True,True),
 (0x49c910,40,'model_scene_name_finalize',2,'void',True,True),(0x490a60,47,'model_object_base_construct',0,'word',False,True),
 (0x4b7b30,18,'model_object_construct',0,'word',False,True),(0x4b7ed0,43,'model_object_bind_scene',1,'void',False,True),
 (0x4d3ce0,33,'model_render_cache_reset',0,'void',False,False)]
instructions=[]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
 instructions += [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in code[a]]
(folder/'scene-finalize-instructions.txt').write_text('\n'.join(instructions)+'\n')
exports += [[0x64a434,'thug_model_mesh_node_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft'],[0x6492e4,'thug_model_object_base_methods_draft'],[0x64a490,'thug_model_object_pc_methods_draft']]
# Explicit-list and valid mesh storage builders; payloads are never substituted.
def linked(g,values):
 head=g.alloc(20);g.put(head,'<5I',0x64a438,0xffffffff,0,head,head);nodes=[]
 for value in values:
  p=g.alloc(20);tail=g.word(head+16);g.put(p,'<5I',0x64a434,value,0,head,tail);g.put(tail+12,'<I',p);g.put(head+16,'<I',p);nodes.append(p)
 return head,nodes
def mesh(g,i=0,material=True,ready=True,n=5):
 p=g.alloc(216);m=g.alloc(64) if material else 0;v=g.alloc(36);data=g.alloc(n+16)
 g.put(p+0x14,'<I',m);g.put(p+0x44,'<I',i%3);g.put(p+0xcc,'<I',v)
 if m:g.put(m+12,'<B',i%3);g.put(m+0x1c,'<f',float(i%5-2));g.put(m+0x20,'<I',0x40 if i%2 else 0)
 g.put(v,'<9I',n,0,INDEXDEV if ready else 0,data,0,0,0xffffffff,4,0);g.data[data-BASE:data-BASE+n]=bytes((k*7+i)&255 for k in range(n));return p,m,v
for fn in [0x4b5ec0,0x4b5e50,0x4b5e90]:
 for n in [0,1,3]:
  for which in [0,1,2]:
   for flags in ([0] if fn==0x4b5ec0 else [0,1,2,0xffffffff]):
    g=Graph();head,nodes=linked(g,[P+0x100+i*16 for i in range(n)]);target=[head]+nodes;target=target[which%len(target)]
    run(g,[call(fn,target,[] if fn==0x4b5ec0 else [flags])],f'list delete{fn:x}/n{n}/which{which}/flags{flags}')
for n in [0,1,2,3,4,5,31,32,33]:
 for ready in [False,True]:
  g=Graph();m,_,v=mesh(g,ready=ready,n=n);g.put(INDEXDEV,'<2I',INDEXVT,7);aux=g.alloc(16);g.put(aux,'<4I',INDEXDEV,3,100,INDEXDEV+0x100)
  run(g,[call(0x4d3e50,m,[aux])]*2,f'shared vertex size{n}/ready{ready}')
for n in [0,1,3,9]:
 for shared in [False,True]:
  for existing in [False,True]:
   g=Graph();values=[mesh(g,i,ready=not shared)[0] for i in range(n)];head,nodes=linked(g,values);g.put(P+0x38,'<3I',head,P+0x800 if existing else 0,0xabcd)
   aux=g.alloc(16);g.put(aux,'<4I',INDEXDEV,0,1024,INDEXDEV+0x100);g.put(INDEXDEV,'<2I',INDEXVT,0)
   run(g,[call(0x4b5360,P,[aux if shared else 0])],f'geometry finish n{n}/shared{shared}/existing{existing}')
for n in [0,1,3,9]:
 for flag in [0,1,256,257]:
  g=Graph();values=[mesh(g,i,material=(i%3!=0))[0] for i in range(n)];array=g.alloc(max(n,1)*4);out=g.alloc(256)
  for i,v in enumerate(values):g.put(array+i*4,'<I',v)
  g.put(P+0x1c,'<6I',out,2,3,1,0,0);scene=g.alloc(644);geometry=g.alloc(100);g.put(scene+0x280,'<I',P);g.put(geometry+0x34,'<4I',scene,0,array,n)
  run(g,[call(0x4dddf0,P,[n,array]),call(0x4dde20,P,[n,array]),call(0x4b44d0,geometry,[flag])],f'count-fill n{n}/flag{flag}')
for n in [0,0xffffffff,0x80000000,1,3,17]:
 g=Graph();g.put(P+0x20,'<I',n);calls=[call(0x4de3e0,P)]
 if n>=0x80000000:calls += [call(0x4dddf0,P,[n,0]),call(0x4dde20,P,[n,0])]
 run(g,calls,f'allocate signed count{n:x}')
# Every priority/alpha/flag/shader/material-address comparator decision.
for px,py in [(0,0),(0x3f800000,0),(0,0x3f800000),(0x7fc12345,0),(0,0x7fa43210),(0x7f800000,0x7f800000)]:
 for ax,ay in [(0,0),(0,1),(1,0),(1,2)]:
  for fx,fy in [(0,0),(0x10,0),(0,0x10),(0x10,0x10)]:
   g=Graph();left,lm,_=mesh(g,0);right,rm,_=mesh(g,1);a=g.alloc(8);g.put(a,'<2I',left,right)
   g.put(lm+0x1c,'<I',px);g.put(rm+0x1c,'<I',py);g.put(lm+12,'<B',ax);g.put(rm+12,'<B',ay);g.put(lm+0x20,'<I',fx);g.put(rm+0x20,'<I',fy)
   run(g,[call(0x4ddd50,0,[a,a+4]),call(0x4ddd50,0,[a+4,a]),call(0x4ddd50,0,[a,a])],f'compare p{px:x}/{py:x}/a{ax}/{ay}/f{fx}/{fy}')
for same in [False,True]:
 for sx,sy in [(0,0),(0,1),(1,0),(0xffffffff,1),(1,0xffffffff)]:
  g=Graph();left,lm,_=mesh(g,0);right,rm,_=mesh(g,0);a=g.alloc(8);g.put(a,'<2I',left,right);g.put(left+0x44,'<I',sx);g.put(right+0x44,'<I',sy)
  if same:g.put(right+0x14,'<I',lm)
  run(g,[call(0x4ddd50,0,[a,a+4]),call(0x4ddd50,0,[a+4,a])],f'compare shader{sx}/{sy}/same{same}')
rng=random.Random(0x4ddfa0)
for n in [0,1,2,3,8,9,17,33,65]:
 for mode in ['forward','reverse','random','same']:
  g=Graph();values=[mesh(g,0 if mode=='same' else i)[0] for i in range(n)]
  if mode=='reverse':values.reverse()
  if mode=='random':rng.shuffle(values)
  array=g.alloc(max(n,1)*4)
  for i,v in enumerate(values):g.put(array+i*4,'<I',v)
  g.put(P+0x1c,'<6I',array,n,99,77,55,33);g.put(P+0x34,'<I',88)
  run(g,[call(0x4ddfa0,P)]*2,f'sort n{n}/{mode}')
g=Graph();v,_,_=mesh(g,material=False);a=g.alloc(4);g.put(a,'<I',v);g.put(P+0x1c,'<2I',a,1);run(g,[call(0x4ddfa0,P)],'sort single null material')
for sectors in [0,1,3]:
 for n in [0,1,3]:
  for shared in [False,True]:
   g=Graph();header=g.alloc(132);g.data[header-BASE:header-BASE+132]=bytes(132);rows=[]
   for si in range(sectors):
    sector=g.alloc(52);geometry=g.alloc(100);values=[mesh(g,i+si,ready=not shared)[0] for i in range(n)];head,nodes=linked(g,values)
    g.put(geometry+0x34,'<4I',P,head,0,n);g.put(sector+0x14,'<I',geometry);rows.append((si+1,sector))
   table=g.table(rows);g.put(P,'<I',0x64a6b8);g.put(P+0xd0,'<I',table);g.put(P+0x280,'<I',header);aux=g.alloc(16);g.put(aux,'<4I',0,99,4096,0)
   name=g.alloc(16);g.data[name-BASE:name-BASE+7]=b'model\n\0'
   run(g,[call(0x49c910,P,[name,aux if shared else 0])],f'finalize sectors{sectors}/meshes{n}/shared{shared}')
for fill in [0,0xa5,0xff]:
 for fn in [0x490a60,0x4b7b30]:
  g=Graph();g.data[P-BASE:P-BASE+200]=bytes([fill])*200;run(g,[call(fn,P)]*2,f'model ctor{fn:x}/fill{fill}')
for value in [0,P,0xffffffff]:
 g=Graph();g.put(P+0x14,'<I',value);run(g,[call(0x4a2ba0,P)],f'geometry getter{value:x}')
g=Graph();scene=g.alloc(644);header=g.alloc(132);g.put(scene+0x280,'<I',header);g.put(header+0x74,'<2I',0x12345678,0x87654321);run(g,[call(0x4b7ed0,P,[scene])]*2,'bind model scene')
for fill in [0,0x12345678,0xffffffff]:
 for i in range(6):defaults[len(defaults)-6+i]=fill
 run(Graph(),[call(0x4d3ce0)]*2,f'cache reset byte plus words{fill:x}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
scope='Original mesh-list disposal, shared vertex binding, geometry finalization, scene render-list count/fill/sort, scene naming/finalization, model construction/binding and render-cache reset. Existing original CRT sort is reused. Explicit GPU providers; valid lists/materials and initialized successful heap are internal contracts.'
fixture={'base':BASE,'memory':'scene-finalize-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'native_callbacks':[{'module':'scene-finalize-ports.wasm','export':'fixture_index_'+n,'slots':slots} for n,slots in [('create',[DVT+0x68,DVT+0x6c]),('lock',[INDEXVT+0x2c]),('unlock',[INDEXVT+0x30])]]+[{'module':'scene-finalize-ports.wasm','export':'fixture_shared_add_ref','slots':[INDEXVT+4]}],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-finalize-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'scene-finalize-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
