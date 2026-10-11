"""Compare original PC geometry spheres, merging, and renderer cache behavior."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved initialized comparison arena>','exec'))
import random
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x4b4760,68,'model_geometry_sphere_pc'),(0x48de90,17,'model_geometry_sphere'),
 (0x4bae30,524,'model_renderer_sphere_pc'),(0x492f30,85,'model_renderer_sphere')]
for a,n,name in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':True,'result':'word','cleanup':4,'memory':False}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
exports += [[0x64a368,'thug_model_geometry_lights_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft']]
OUT=P+0x800
def geometry(g,values,mode=2):
 geometry=g.alloc(100);instance=g.alloc(100);header=g.alloc(132)
 g.put(geometry,'<I',0x64a368);g.put(geometry+0x4c,'<I',instance if mode else 0)
 g.put(instance+0x58,'<I',header if mode==2 else 0);g.put(header+0x64,'<4I',*values)
 return geometry,instance,header
def renderer(g,spheres,flags=0,mode=2):
 head=g.alloc(12);nodes=[head]+[g.alloc(12) for _ in spheres]
 for i,node in enumerate(nodes):
  part=g.alloc(24);geom,_,_=geometry(g,spheres[i-1] if i else [0]*4,mode)
  g.put(part,'<I',geom);g.put(node,'<3I',part,nodes[(i+1)%len(nodes)],nodes[i-1])
 g.put(P,'<I',0x64a4b4);g.put(P+0x10,'<2I',head,len(spheres));g.put(P+0x44,'<B',flags);g.put(P+0x46,'<H',len(spheres))
 return nodes
def check(g,calls,label,quiet=(),arithmetic=()):
 steps=run(g,calls,label)
 for s in steps:
  if quiet:s['quiet_float_fields']=list(quiet)
  if arithmetic:s['float_fields']=list(arithmetic)
 return steps
patterns=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x4b000001,0xcb000001,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffa43210]
for fn in [0x4b4760,0x48de90]:
 for mode in [0,1,2]:
  for value in patterns:
   g=Graph();geom,instance,header=geometry(g,[value,value^0x80000000,value,value^0x80000000],mode)
   check(g,[call(fn,geom,[OUT])],f'geometry {fn:x}/mode{mode}/bits{value:x}',quiet=[OUT+o for o in [4,8,12]] if mode==2 else [])
 # Overlap the header bounds and the geometry itself; source loads precede writes.
 for off in [-8,-4,0,4,8,12]:
  g=Graph();geom,instance,header=geometry(g,[0x7fa12345,0xffa43210,0x80000000,0x7f812345]);out=header+0x64+off
  check(g,[call(fn,geom,[out])],f'geometry overlap{fn:x}/{off}',quiet=[out+o for o in [4,8,12]])
 for off in [0,4,0x48,0x4c]:
  g=Graph();geom,_,_=geometry(g,[0x7fa12345,0xffa43210,0x80000000,0x7f812345]);out=geom+off
  check(g,[call(fn,geom,[out])],f'geometry receiver overlap{fn:x}/{off}',quiet=[out+o for o in [4,8,12]])
def bits(values):return list(struct.unpack('<4I',struct.pack('<4f',*values)))
shapes=[[],[[0,0,0,1]],[[0,0,0,10],[1,0,0,1]],[[0,0,0,1],[1,0,0,10]],
 [[0,0,0,1],[4,0,0,1]],[[1,2,3,2],[-5,8,-10,7]],[[0,0,0,1],[0,0,0,1]],
 [[0,0,0,3],[2,0,0,1]],[[0,0,0,-3],[2,0,0,-1]],
 [[-7,2,1,2],[10,-8,3,4],[2,5,19,6],[0,0,0,0]]]
for fn in [0x4bae30,0x492f30]:
 for mode in [0,1,2]:
  for i,shape in enumerate(shapes):
   g=Graph();renderer(g,[bits(v) for v in shape],flags=0xa4,mode=mode)
   check(g,[call(fn,P,[OUT])]*2,f'sphere {fn:x}/mode{mode}/shape{i}',arithmetic=[OUT+o for o in range(0,16,4)]+([P+o for o in range(0x34,0x44,4)] if fn==0x492f30 else []))
for value in patterns:
 for axis in range(4):
  g=Graph();a=bits([1,-2,3,5]);b=bits([-4,6,-7,2]);b[axis]=value;renderer(g,[a,b])
  check(g,[call(0x4bae30,P,[OUT])],f'merge exceptional axis{axis}/{value:x}',arithmetic=[OUT+o for o in range(0,16,4)])
rng=random.Random(0x4bae30)
for i in range(120):
 g=Graph();spheres=[[rng.getrandbits(32) for _ in range(4)] for j in range(1+i%5)];renderer(g,spheres)
 if len(spheres)==1:
  check(g,[call(0x492f30,P,[OUT])]*2,f'merge raw random{i}',quiet=[OUT+o for o in [0,4,8]]+[P+o for o in [0x34,0x38,0x3c]],arithmetic=[OUT+12,P+0x40])
 else:
  check(g,[call(0x492f30,P,[OUT])]*2,f'merge raw random{i}',arithmetic=[OUT+o for o in range(0,16,4)]+[P+o for o in range(0x34,0x44,4)])
# Cached reads copy raw bits, including signaling NaNs; live forward overlap.
for flags in [1,3,255]:
 for off in [-12,-4,0,4,8,12,0x100]:
  g=Graph();renderer(g,[],flags);g.put(P+0x34,'<4I',0x7fa12345,0xff812345,0x80000000,0xdeadbeef)
  check(g,[call(0x492f30,P,[P+0x34+off])],f'cached flags{flags}/overlap{off}')
# A high unsigned count still follows list links, rather than indexing by count.
for count in [0x8000,0xffff]:
 g=Graph();renderer(g,[bits([2,4,8,16])]);g.put(P+0x46,'<H',count)
 check(g,[call(0x4bae30,P,[OUT])],f'unsigned nonzero count{count}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
for case in oracle.cases:
 for at,data in case.get('patches',[]):
  if int.from_bytes(bytes.fromhex(data),'little') in {e[0] for e in exports}:fields.add(at)
scope='Four original routines recover geometry sphere access and virtual forwarding, multi-part sphere merging with x87 operation/spill order, and renderer bounds caching. Actual PC virtuals execute. Geometry getter quieting checks preserve NaN sign/payload exactly; only merged arithmetic outputs permit NaN classification. Cached raw copies including NaNs and live forward overlap compare exactly. Complete arena, globals, returns and preserved registers compare. A nonzero part count requires a valid nonempty circular list. No drawing or playable game is supplied.'
fixture={'base':BASE,'memory':'renderer-bounds-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'renderer-bounds-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'scope':scope}
(folder/'renderer-bounds-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
