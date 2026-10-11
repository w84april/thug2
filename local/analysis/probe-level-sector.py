"""Original billboard preparation and material registration, bounded inputs."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-vertex-upload.py').read_text().split('\nspecs=')[0],'<preserved vertex fixture setup>','exec'))
import random
exports += [[0x64a894,'thug_material_node_methods'],[0x64a898,'thug_material_sentinel_methods']]
specs=[(0x4d7580,1373,'thug_mesh_billboard_prepare_draft',3),(0x4cebe0,193,'thug_material_table_add_mesh_draft',1)]
for a,n,name,argc in specs:
 functions[hex(a)]={'name':name,'this':True,'result':'void','cleanup':argc*4,'memory':True}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
initial=bytes(memory);oracle.initial=initial
DATA,VDATA,IDATA,PIVOT,AXIS=P+0x1000,P+0x300,P+0x400,P+0x600,P+0x700
float_fields=set()
def billboard(label,kind=1,axis=(0,1,0,0),pivot=(0,0,0,0),vertices=((0,0,0),(1,0,0),(0,1,0),(1,1,0)),order=(0,1,2,3),stride=36,lock=0,bits=None):
 g=Graph();g.put(P,'<I',0x20040);g.put(P+0x18,'<B',stride);g.put(P+0xcc,'<I',VDATA);g.put(P+0x54,'<I',IDATA)
 g.put(VDATA,'<9I',4*stride,0,INDEXDEV+0x8000,DATA,0x12345678,0x98765432,0,0,0)
 indexbytes=g.alloc(8);g.put(indexbytes,'<4H',*order);g.put(IDATA,'<6I',8,0,0x65,INDEXDEV,indexbytes,0)
 g.put(INDEXDEV,'<I',INDEXVT);g.put(INDEXCTL+12,'<I',lock);g.put(INDEXCTL+24,'<I',int(lock<0x80000000))
 g.put(PIVOT,'<4f',*pivot);g.put(AXIS,'<4f',*axis)
 for i,v in enumerate(vertices):
  g.put(DATA+i*stride,'<3f',*v);float_fields.update(DATA+i*stride+j*4 for j in range(3))
 if bits is not None:g.put(DATA+stride+4,'<I',bits)
 run(g,[call(0x4d7580,P,[kind,PIVOT,AXIS])],label)
 assert oracle.word(P)&0x10 and oracle.word(VDATA+24)==0xffffffff
for kind in [1,2]:
 for axis in [(0,1,0,0),(1,0,0,0),(0,0,1,0),(1,.99,0,1),(1,1,1,0),(0,-1,0,0)]:
  for lock in [0,1,0xffffffff,0x80000000]:billboard(f'kind{kind}/axis{axis}/lock{lock:x}',kind=kind,axis=axis,lock=lock)
for bits in [0,0x3f7d70a3,0x3f7d70a4,0x3f7d70a5,0xbf7d70a3,0xbf7d70a4,0xbf7d70a5,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]:
 y=struct.unpack('<f',struct.pack('<I',bits))[0];billboard(f'type threshold{bits:x}',kind=2,axis=(1,y,0,0))
for stride in [12,16,28,36,44,60]:
 for order in [(0,1,2,3),(0,2,1,3),(2,3,0,1),(0,0,0,0)]:billboard(f'stride{stride}/indices{order}',stride=stride,order=order,pivot=(.1,-11,2,1))
for value in [0,1e-40,1e-20,1e20,1e38]:
 for kind in [1,2]:billboard(f'normal exponent{value}/kind{kind}',kind=kind,vertices=((0,0,0),(value,0,0),(0,value,0),(value,value,0)))
for bits in [0,0x80000000,1,0x80000001,0x7fffff,0x800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]:
 for kind in [1,2]:billboard(f'nonfinite/edge{bits:x}/kind{kind}',kind=kind,bits=bits)
rng=random.Random(0x4d7580)
for i in range(80):
 vertices=[tuple(rng.uniform(-1e5,1e5) for j in range(3)) for k in range(4)];pivot=tuple(rng.uniform(-1e5,1e5) for j in range(3))+(0,)
 billboard(f'random finite{i}',kind=1+i%2,axis=(1,0,1,0) if i%3 else (0,1,0,0),vertices=vertices,pivot=pivot)
# Material registration: textured gate, all3 lists, duplicates and sort order.
for count in [0,1,4,12]:
 for mode in ['normal','null material','no texture']:
  g=Graph();table=P+0x1800;g.put(table,'<I',0);calls=[]
  for i in range(count+2):
   mat=g.alloc(0x110);g.put(mat+8,'<I',1+i%4);g.put(mat+0x1c,'<f',float((count-i)%5));g.put(mat+0x30,'<I',0 if mode=='no texture' else 0x12345678)
   record=g.alloc(36);g.put(record,'<I',i%3);mesh=g.alloc(216);g.put(mesh+0x14,'<I',0 if mode=='null material' else mat);g.put(mesh+0x4c,'<I',record)
   calls += [call(0x4cebe0,table,[mesh])]*2
  run(g,calls,f'material count{count}/mode{mode}')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
excluded={'0x4d7580':{'0x4d7595':'initialized allocator contract','0x4d793c':'unreachable for serialized kinds1/2 with no external record mutation'},'0x4cebe0':{'0x4cec27':'initialized allocator contract','0x4cec5a':'successful allocation contract'}}
for at,c in coverage.items():c['excluded']=excluded[at];assert set(c['missing'])==set(c['excluded'])
print('COVERAGE',json.dumps(coverage),flush=True)
prior=json.loads((folder/'vertex-upload-fixtures.json').read_text())
scope='Original billboard4d7580 for valid serialized kinds1/2, four accessible vertices and successful initialized allocation; exact x87 PC24/spill order, index re-upload, local vertex basis and CPU-only vertex unlock. Original material registration4cebe0 with real group construction, list insertion and recovered CRT sort. Only resulting NaN vertex coordinates permit classification comparison.'
fixture={**prior,'memory':'level-sector-memory.bin','globals':globals_,'functions':functions,'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'float_fields':sorted(float_fields),'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-sector-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'scope':scope}
(folder/'level-sector-original.json').write_text(json.dumps(report,indent=2)+'\n');print('REPORT',len(labels),sum(oracle.counts.values()),flush=True)
