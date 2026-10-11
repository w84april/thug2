"""Original geometry helpers on actual loader-built training collision edges."""
import hashlib,json,math,struct
from collections import Counter
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';v=ROOT/'local/validation/collision';sha=lambda data:hashlib.sha256(data).hexdigest()
prior=json.loads((p/'sphere-geometry-checkpoint.json').read_text())
selection=json.loads((p/'sphere-geometry-training-original.json').read_text())
loaded_path=ROOT/selection['loaded_collision'];loaded=loaded_path.read_bytes()
assert sha(loaded)==prior['artifact_hashes'][str(loaded_path.relative_to(ROOT))]
BASE=0x1000000;SIZE=0x94000;CAP=BASE+0x90000;SPHERE=BASE+0x92000
A=SPHERE+32;B=A+16;DISPLACEMENT=B+32;POINTS=DISPLACEMENT+32;COUNT=POINTS+64
memory=bytearray(b'\xa5'*SIZE);memory[:len(loaded)]=loaded;initial=bytes(memory)
functions={
 '0x40b2d0':{'name':'thug_collision_vertex_into','this':True,'result':'void','stack_args':[0,1],'cleanup':8},
 '0x4032a0':{'name':'thug_capsule_from_segment_draft','this':True,'result':'word','stack_args':[0,1],'cleanup':8,'float_args':[1]},
 '0x403330':{'name':'thug_capsule_point_draft','this':True,'result':'byte','stack_args':[0,1],'cleanup':8},
 '0x40e280':{'name':'thug_segment_sphere_intersections_draft','this':False,'result':'byte','stack_args':list(range(4)),'cleanup':0}}
oracle=ScriptHeapOracle(initial,BASE,BASE+0x93000,BASE+0x93200,[],[],functions,observe=[0x40b2d0,0x4032a0,0x403330,0x402d60,0x40e280,0x4024d0,0x402440,0x402320])
def word(at):return struct.unpack_from('<I',loaded,at-BASE)[0]
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def vertex(obj,index):
 pointer=word(obj+0x30)
 if loaded[obj-BASE+11]:
  offsets=struct.unpack_from('<3H',loaded,pointer-BASE+index*6);lower=struct.unpack_from('<3f',loaded,obj-BASE+16)
  return [f32(offsets[i]/16+lower[i]) for i in range(3)]
 return list(struct.unpack_from('<3f',loaded,pointer-BASE+index*12))
labels=[];outcomes=Counter()
for selected in selection['selected_triangles']:
 index=selected['object_index'];obj=BASE+32+index*64;ids=selected['vertices'];a,b,c=[vertex(obj,j) for j in ids]
 e=[b[j]-a[j] for j in range(3)];f=[c[j]-a[j] for j in range(3)]
 n=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]];length=math.sqrt(sum(x*x for x in n));n=[x/length for x in n]
 for height in [0.,8.,32.]:
  center=[f32((a[j]+b[j])/2+height*n[j]) for j in range(3)]+[0.,16.]
  patches=[[SPHERE,struct.pack('<5f',*center).hex()]]
  calls=[(0x40b2d0,obj,[ids[0],A]),(0x40b2d0,obj,[ids[1],B]),(0x4032a0,CAP,[A,bits(16.)]),(0x403330,CAP,[SPHERE,DISPLACEMENT]),(0x40e280,0,[A,SPHERE,COUNT,POINTS])]
  oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
  steps=oracle.case(calls,patches)
  outcomes[f'height{height}/capsule{steps[-2]["result"]}/intersection{steps[-1]["result"]}']+=1
  labels.append(f'actual training object{index}/face{selected["face"]}/edgeAB/height{height}')
 if len(labels)%300==0:print('Training edge cases',len(labels),flush=True)
scope='Actual loader-built TR collision buffer and the same 561 nondegenerate triangle selections verified previously. Original40b2d0 reads each real AB edge from compressed/uncompressed records; capsule construction, capsule/point displacement and segment/sphere intersections execute on it with radius16 at three normal offsets. All arena bytes and returns compare exactly. Host decoding chooses test sphere positions only. This is edge-geometry integration, not full swept sphere/triangle, scene candidate discovery, complete Rigidbody update, rendered frame or playable level.'
fixture={'base':BASE,'memory':'sphere-sweep-training-memory.bin','globals':[],'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(p/fixture['memory']).write_bytes(initial);(p/'sphere-sweep-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'selected_edges':len(selection['selected_triangles']),'selection_source':'local/analysis/sphere-geometry-training-original.json','selection_source_sha256':sha((p/'sphere-geometry-training-original.json').read_bytes()),'original_collision_objects':selection['original_collision_objects'],'outcomes':dict(outcomes),'loaded_collision':str(loaded_path.relative_to(ROOT)),'loaded_collision_sha256':sha(loaded),'scope':scope,'playable':False}
(p/'sphere-sweep-training-original.json').write_text(json.dumps(report,indent=2)+'\n');print('Original training edges',len(labels),'cases',sum(oracle.counts.values()),'calls',dict(outcomes),flush=True)
