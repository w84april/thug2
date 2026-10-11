"""Compare actual render-instance construction, geometry binding and list insertion."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved initialized heap setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x4d1030,137,'model_render_instance_construct',4,'word',False,True),
 (0x4b54b0,288,'model_geometry_load_instance',3,'byte',True,True),
 (0x492e50,4,'model_renderer_skeleton',0,'word',False,True),
 (0x48ddf0,23,'model_geometry_bind',3,'byte',True,True),
 (0x49f3b0,8,'model_geometry_flag16',1,'byte',False,True),
 (0x4964a0,99,'model_part_insert',2,'void',True,True)]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
exports += [[0x64a368,'thug_model_geometry_lights_methods_draft']]
globals_.append(['thug_model_render_instances_draft',0x7825c0,4]);defaults.append(0)
oracle.globals=globals_;oracle.defaults=defaults
def scene(g,count,formats,flags,bones):
 header=g.alloc(132);array=g.alloc(max(count,1)*4);g.put(header+0x1c,'<2I',array,count);g.put(header+0x78,'<I',bones)
 for i in range(count):
  mesh=g.alloc(64);g.put(mesh,'<I',flags[i%len(flags)]);g.put(mesh+0x38,'<I',formats[i%len(formats)]);g.put(array+i*4,'<I',mesh)
 return header
bits=[0,0x80000000,0x3f800000,0x7f800000,0xff800000,0x7fa12345,0x7fc54321,1,0xdeadbeef,0x87654321,0xffffffff,0x3f000000,0x40000000,0xbf800000,0x00800000,0x007fffff]
shapes=[(0,[0],[0]),(1,[0],[0]),(1,[0x10],[0]),(1,[0x10],[0x20000]),(3,[0x10],[0]),(3,[0x10,0],[0]),(3,[0x10],[0,0x20000]),(3,[0x10,0x10,0],[0])]
for fill in [0,0xa5,0xff]:
 for count,formats,flags in shapes:
  for bones,header_bones in [(0,0),(P+0x400,0),(P+0x400,1),(P+0x400,0xffffffff)]:
   g=Graph();g.data[P-BASE:P-BASE+100]=bytes([fill])*100;header=scene(g,count,formats,flags,header_bones);matrix=g.alloc(64);g.put(matrix,'<16I',*bits)
   defaults[-1]=P+0x500
   run(g,[call(0x4d1030,P,[header,matrix,P+0x300,bones])],f'instance fill{fill}/n{count}/format{formats}/flags{flags}/bones{bones:x}/{header_bones:x}')
for count in [0xffffffff,0x80000000]:
 g=Graph();header=scene(g,0,[0],[0],0);g.put(header+0x20,'<I',count);matrix=g.alloc(64);g.put(matrix,'<16I',*bits);defaults[-1]=0
 run(g,[call(0x4d1030,P,[header,matrix,0,0])],f'instance negative signed count{count:x}')
for offset in [-8,-4,0,4,8,16]:
 g=Graph();header=scene(g,0,[0],[0],0);g.put(P+offset,'<16I',*bits);defaults[-1]=0
 run(g,[call(0x4d1030,P,[header,P+offset,0,0])],f'instance forward matrix overlap{offset}')
for fn in [0x4b54b0,0x48ddf0]:
 for skin in [0,1,255,256,257,0xffffffff]:
  for count in [0,1,3]:
   g=Graph();header=scene(g,count,[0x10],[0],0);model=g.alloc(200);s=g.alloc(644);renderer=g.alloc(80)
   g.put(model+0xc4,'<I',s);g.put(s+0x280,'<I',header);g.put(renderer+8,'<2I',P+0x300,P+0x400);g.put(P,'<I',0x64a368);defaults[-1]=0
   run(g,[call(fn,P,[model,renderer,skin])]*2,f'geometry bind{fn:x}/skin{skin:x}/n{count}')
for value in [0,1,P,0xffffffff]:
 g=Graph();g.put(P+12,'<I',value);run(g,[call(0x492e50,P)],f'renderer skeleton getter{value:x}')
for flag in [0,1,255,256,0xffffffff]:
 g=Graph();g.put(P,'<I',0x64a368);run(g,[call(0x49f3b0,P,[flag])],f'actual PC flag virtual{flag:x}')
for count in [0,1,3]:
 for position in range(count+1):
  for value in [0,P+0x100,0xffffffff]:
   g=Graph();head=g.alloc(12);nodes=[head]+[g.alloc(12) for _ in range(count)]
   for i,node in enumerate(nodes):g.put(node,'<3I',0x12340000+i,nodes[(i+1)%len(nodes)],nodes[i-1])
   g.put(P,'<2I',head,count);slot=g.alloc(4);g.put(slot,'<I',value)
   run(g,[call(0x4964a0,P,[nodes[position],slot])]*3,f'part insert n{count}/position{position}/value{value:x}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
scope='Six original routines construct render instances, link their global registry, classify eligible meshes, bind model scenes through real geometry virtuals, read renderer skeletons, dispatch the original PC flag method and insert renderer part-list nodes. Exact raw matrix bits including NaNs, forward overlap, poisoned retained bytes, unsigned flags, signed counts, early exits and list insertion order compare against original instructions. Initialized successful heap and valid internal graphs are required. No drawing or game success is supplied.'
fixture={'base':BASE,'memory':'render-instance-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'render-instance-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'render-instance-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
