"""Original vertex access and sphere contact on the loader-built training data."""
import hashlib,json,math,struct
from collections import Counter
from pathlib import Path
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';v=ROOT/'local/validation/collision';sha=lambda data:hashlib.sha256(data).hexdigest()
prior=json.loads((p/'rigidbody-solver-checkpoint.json').read_text())
loader=json.loads((v/'loading-fixtures.json').read_text())['datasets'][0]
loaded_path=v/loader['loaded'];loaded=loaded_path.read_bytes()
assert sha(loaded)==prior['artifact_hashes'][str(loaded_path.relative_to(ROOT))]
BASE=0x1000000;SIZE=0x94000;PROBE=BASE+0x90000;POINT=BASE+0x92000
A=POINT+32;B=A+32;C=B+32;OUT=C+32;NORMAL=OUT+32
memory=bytearray(b'\xa5'*SIZE);memory[:len(loaded)]=loaded;initial=bytes(memory)
functions={
 '0x40b2d0':{'name':'thug_collision_vertex_into','this':True,'result':'void','stack_args':[0,1],'cleanup':8},
 '0x418330':{'name':'thug_sphere_probe_construct_draft','this':True,'result':'word','stack_args':[0,1],'cleanup':8,'float_args':[1]},
 '0x40f9e0':{'name':'thug_sphere_triangle_draft','this':False,'result':'byte','stack_args':list(range(6)),'cleanup':0}}
oracle=ScriptHeapOracle(initial,BASE,BASE+0x93000,BASE+0x93200,[],[],functions,
 observe=[0x40b2d0,0x403210,0x418330,0x40f9e0,0x40b860,0x4023f0])
def word(at):return struct.unpack_from('<I',loaded,at-BASE)[0]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def vertex(obj,index):
 pointer=word(obj+0x30)
 if loaded[obj-BASE+11]:
  offsets=struct.unpack_from('<3H',loaded,pointer-BASE+index*6)
  lower=struct.unpack_from('<3f',loaded,obj-BASE+16)
  return [f32(offsets[i]/16+lower[i]) for i in range(3)]
 return list(struct.unpack_from('<3f',loaded,pointer-BASE+index*12))
labels=[];selected=[];outcomes=Counter();skipped=[]
for index in range(loader['count']):
 obj=BASE+32+index*64;count=struct.unpack_from('<H',loaded,obj-BASE+8)[0]
 small=loaded[obj-BASE+10];faces=word(obj+12);chosen=None
 for face in range(count):
  ids=struct.unpack_from('<3B' if small else '<3H',loaded,faces-BASE+face*(8 if small else 10)+4)
  vertices=[vertex(obj,j) for j in ids];a,b,c=vertices
  e=[b[j]-a[j] for j in range(3)];f=[c[j]-a[j] for j in range(3)]
  normal=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]]
  length=math.sqrt(sum(x*x for x in normal))
  if length>1e-8:
   chosen=(face,ids,vertices,[x/length for x in normal]);break
 if chosen is None:skipped.append(index);continue
 face,ids,vertices,normal=chosen
 selected.append({'object_index':index,'checksum':hex(word(obj)),'face':face,'vertices':list(ids),
  'small_faces':bool(small),'small_vertices':bool(loaded[obj-BASE+11])})
 center=[sum(a[j] for a in vertices)/3 for j in range(3)]
 for height in [8.,-8.,32.]:
  position=[f32(center[j]+height*normal[j]) for j in range(3)]+[0.]
  patch=[[POINT,struct.pack('<4f',*position).hex()]]
  calls=[(0x40b2d0,obj,[j,out]) for j,out in zip(ids,[A,B,C])]
  calls += [(0x418330,PROBE,[POINT,bits(16.)]),(0x40f9e0,0,[PROBE,A,B,C,OUT,NORMAL])]
  oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
  steps=oracle.case(calls,patch);outcomes[f'height{height}/result{steps[-1]["result"]}']+=1
  labels.append(f'actual training object{index}/face{face}/height{height}')
 if len(selected)%100==0:print('Training collision objects',len(selected),flush=True)
scope='Actual loader-built TR collision buffer, with one nondegenerate triangle selected from each available collision object. The original vertex accessor reads the real compressed/uncompressed records and feeds the recovered sphere constructor and stationary sphere/triangle routine. Positive, negative and distant plane offsets compare all arena bytes, normals, closest points and return values exactly. This is a triangle-contact integration check, not scene candidate discovery, complete Rigidbody update, rendered frame or playable level.'
fixture={'base':BASE,'memory':'sphere-geometry-training-memory.bin','globals':[],'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(p/fixture['memory']).write_bytes(initial)
(p/'sphere-geometry-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'original_collision_objects':loader['count'],
 'selected_triangles':selected,'skipped_without_nondegenerate_triangle':skipped,'outcomes':dict(outcomes),
 'loaded_collision':str(loaded_path.relative_to(ROOT)),'loaded_collision_sha256':sha(loaded),'scope':scope,'playable':False}
(p/'sphere-geometry-training-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('Original training geometry',len(labels),'cases',sum(oracle.counts.values()),'calls',len(selected),'triangles',dict(outcomes),'skipped',skipped,flush=True)
