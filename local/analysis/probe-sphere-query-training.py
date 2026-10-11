"""Full queries through the original loader-built TR collision grid and objects."""
import hashlib,importlib.util,json,math,struct
from collections import Counter
from specimen import ROOT
spec=importlib.util.spec_from_file_location('sphere_query_support',ROOT/'local/analysis/sphere-query-support.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
p=ROOT/'local/analysis';v=ROOT/'local/validation/collision';sha=lambda data:hashlib.sha256(data).hexdigest()
prior=json.loads((p/'sphere-contact-checkpoint.json').read_text());loading=json.loads((v/'loading-fixtures.json').read_text());d=loading['datasets'][0];a=loading['addresses']
sources={};blobs={}
for key in ['loaded','heap','grid']:
 path=v/d[key];data=path.read_bytes();name=str(path.relative_to(ROOT));assert sha(data)==prior['artifact_hashes'][name]
 sources[name]=sha(data);blobs[key]=data
BASE=a['data'];HEAP=BASE+0x90000;GRID=BASE+0xa0000;PROBE=BASE+0xb0000;RESULT=PROBE+0x14;CACHE=BASE+0xb2000;POINT=BASE+0xb4000;SCENE=BASE+0xb9000;NODES=BASE+0xba000;SIZE=0xbc000
memory=bytearray(b'\xa5'*SIZE);memory[:len(blobs['loaded'])]=blobs['loaded'];memory[HEAP-BASE:HEAP-BASE+len(blobs['heap'])]=blobs['heap'];memory[GRID-BASE:GRID-BASE+len(blobs['grid'])]=blobs['grid']
delta=HEAP-a['heap'];INST=d['instances']+delta;relocations=[]
def word(at):return struct.unpack_from('<I',memory,at-BASE)[0]
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def w(at,*values):put(at,'<'+'I'*len(values),*values)
# Compact only the heap and grid addresses, preserving every geometry byte.
# Rewrite documented cell-list pointers and their instance pointers, never
# search/replace arbitrary words. Both original and Wasm receive this same arena.
for i in range(400):
 cell=GRID+0x30+i*48;count=word(cell+0x24);old=word(cell+0x2c)
 if not old:assert count==0;continue
 assert a['heap']<=old<a['heap']+len(blobs['heap'])
 w(cell+0x2c,old+delta);relocations.append([cell+0x2c,old,old+delta])
 for j in range(count):
  at=old+delta+j*4;value=struct.unpack_from('<I',blobs['heap'],old-a['heap']+j*4)[0]
  assert d['instances']<=value<d['instances']+24*d['count']
  w(at,value+delta);relocations.append([at,value,value+delta])
w(SCENE+0xd4,GRID);w(NODES+4,SCENE);w(NODES+12,NODES+16);w(NODES+20,0xffffffff)
s.FUNCTIONS['0x418330']={'name':'thug_sphere_probe_construct_draft','this':True,'result':'word','stack_args':[0,1],'cleanup':8,'float_args':[1]}
q=s.Queries(memory,BASE,NODES,[INST+i*24 for i in range(d['count'])]);q.oracle.cpu.hook_add(4,q.oracle.observe,begin=0x418330,end=0x418330)
selected=prior['sphere_contact_training']['selected_triangles'];outcomes=Counter();cache_sizes=[]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def vertex(obj,index):
 pointer=word(obj+0x30)
 if memory[obj-BASE+11]:
  offsets=struct.unpack_from('<3H',memory,pointer-BASE+index*6);lower=struct.unpack_from('<3f',memory,obj-BASE+16)
  return [f32(offsets[j]/16+lower[j]) for j in range(3)]
 return list(struct.unpack_from('<3f',memory,pointer-BASE+index*12))
for selection in selected:
 index=selection['object_index'];obj=BASE+32+index*64;vertices=[vertex(obj,j) for j in selection['vertices']];va,vb,vc=vertices
 e=[vb[j]-va[j] for j in range(3)];f=[vc[j]-va[j] for j in range(3)];normal=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]]
 length=math.sqrt(sum(x*x for x in normal));normal=[x/length for x in normal];center=[sum(a[j] for a in vertices)/3 for j in range(3)]
 for height,speed,travel in [(8.,0.,0.),(32.,-64.,1.)]:
  position=[f32(center[j]+height*normal[j]) for j in range(3)]+[0.];velocity=[f32(speed*n) for n in normal]+[0.]
  # The cache is a fixture over actual objects, broad enough to contain the
  # whole sweep. Discovery in the uncached call still uses the original grid.
  lower=[f32(min(position[j],position[j]+travel*velocity[j])-17) for j in range(3)]
  upper=[f32(max(position[j],position[j]+travel*velocity[j])+17) for j in range(3)]
  entries=[]
  for k in range(d['count']):
   bounds=struct.unpack_from('<8f',memory,32+k*64+16)
   if all(lower[j]<=bounds[j+4] and bounds[j]<=upper[j] for j in range(3)):entries.append(k)
  assert len(entries)<=500;cache_sizes.append(len(entries));cache=bytearray(b'\xa5'*0xfcc)
  struct.pack_into('<8f',cache,0,*lower,1,*upper,1)
  for k,j in enumerate(entries):struct.pack_into('<II',cache,32+k*8,INST+24*j,BASE+32+j*64+16)
  struct.pack_into('<3I',cache,0xfc0,len(entries),len(entries),0)
  patches=[s.floats(POINT,*position),s.floats(PROBE,*position,16),s.floats(RESULT+0x584,*velocity,travel),s.words(RESULT+0x598,0),s.patch(RESULT+0x59c,'<HHI',0x10,0,0),s.words(PROBE+0xb5c,0),[CACHE,cache.hex()]]
  # Constructor would reset travel; its behavior is already covered by the
  # preceding training suites. Here all three full queries receive identical
  # sphere/direction/filter input and retain their own original hit ordering.
  calls=[(0x4110b0,INST+index*24,[PROBE,obj+16,RESULT,s.Q]),(0x410240,0,[PROBE,RESULT,0,s.Q]),(0x418300,PROBE,[0,s.Q])]
  steps=q.check(calls,patches,f'actual training object{index}/height{height}/speed{speed}/static,grid,cache',{q.cache_index:CACHE})
  for label,step in zip(['static','grid','cache'],steps):outcomes[f'{label}/height{height}/result{step["result"]}']+=1
scope='Complete static, uncached scene and default-cache probe sphere queries on actual loader-built TR geometry, 605 instances and the original populated 400-cell grid. One nondegenerate face position from each of561objects, stationary and swept trajectories. Host code chooses positions and forms cache fixtures; all geometric and grid discovery callees execute unchanged. Heap/grid pointers are compactly relocated at documented fields only, identically for original and Wasm. Exact whole-arena/global/return comparisons; no tolerance or NaN classification. Full Rigidbody/scene updates, rendering and original playability remain unfinished.'
q.save('sphere-query-training',scope,{'source_hashes':sources,'relocations':relocations,'original_collision_objects':d['count'],'selected_triangles':selected,'grid_cell_references':d['cell_references'],'grid_nonempty_cells':d['nonempty_cells'],'query_outcomes':dict(outcomes),'cache_candidates_min':min(cache_sizes),'cache_candidates_max':max(cache_sizes)})
