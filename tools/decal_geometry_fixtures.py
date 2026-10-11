"""Original full decal subdivision, including the fall-through after 4b8220."""
import json,random,struct
from collections import Counter
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle

def build_geometry(out):
 base,size=0x1800000,0x40000
 context,manager,mesh,output,dest=base+0x20,base+0x100,base+0x1000,base+0x2000,base+0x4000
 memory=bytearray(b'\xad'*size)
 struct.pack_into('<8I',memory,context-base,base+0x30000,base+size,0,base+0x28000,base,base+size,0,0)
 struct.pack_into('<I',memory,manager-base+0x124,manager+0x200)
 struct.pack_into('<I',memory,output-base,dest)
 initial=bytes(memory);rng=random.Random(0x4b8220)
 globals_=[];defaults=[];indices={}
 for name,at,count in [('thug_decal_work_stack',0x6fc4a0,0x4008),('thug_decal_scratch_vertices',0x7052c0,6*128),('thug_decal_area_threshold',0x67ddf0,4)]:
  for offset in range(0,count,4):
   indices[at+offset]=len(globals_);globals_.append([name,at+offset,4,offset]);defaults.append(0xadadadad)
 functions={'0x4b8220':{'name':'thug_decal_subdivide','this':False,'result':'byte','cleanup':0,'memory':False}}
 oracle=ScriptHeapOracle(initial,base,context,manager,globals_,defaults,functions,observe=[0x4b8220,0x4b8232,0x490d50,0x490d80])
 labels=[];branches=Counter()
 def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
 def vertex(width,xyz,uv):
  data=bytearray(rng.getrandbits(8) for _ in range(width));struct.pack_into('<3f',data,0,*xyz)
  if uv:struct.pack_into('<2f',data,uv,rng.uniform(-4,4),rng.uniform(-4,4))
  return data
 def case(width,records,threshold,color=0,uv=0,steps=1,label='subdivide',extra=()):
  stack=bytearray(b'\xad'*0x4008);struct.pack_into('<2I',stack,0,width*len(records),width)
  for i,data in enumerate(records):stack[8+i*width:8+(i+1)*width]=data
  changes={indices[0x6fc4a0+i]:int.from_bytes(stack[i:i+4],'little') for i in range(0,len(stack),4)}
  changes[indices[0x67ddf0]]=threshold
  patches=[[mesh+0x1c,bytes([color,0,uv]).hex()],*extra]
  oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
  stages=oracle.case([(0x4b8220,0,[output,mesh])]*steps,patches,changes);labels.append(label)
  previous=len(records)*width
  for stage in stages:
   current=stage['globals'][indices[0x6fc4a0]]
   branches['empty' if not previous else 'split' if current>previous else 'emit']+=1;previous=current
   merged=[]
   for at,data in stage['outputs']:
    if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
    else:merged.append([at,data])
   stage['outputs']=merged
  return stages
 case(128,[],bits(1),label='empty stack does not read output or format')
 formats=[(12,0,0),(16,12,0),(24,12,16),(28,0,20),(31,23,12),(127,12,118),(128,116,120)]
 for width,color,uv in formats:
  for side,threshold in [(0,0),(1,bits(1)),(1,bits(1)-1),(1,bits(1)+1),(2,bits(1)),(4,bits(1)),(1,bits(-1))]:
   records=[vertex(width,p,uv) for p in [(0,0,0),(side,0,0),(0,side,0)]]
   case(width,records,threshold,color,uv,label='format offsets, byte tails and exact area threshold')
  records=[vertex(width,p,uv) for p in [(0,0,0),(8,0,0),(0,8,0)]]
  stages=case(width,records,bits(1),color,uv,86,label='drain three subdivision levels, retained stack and scratch bytes')
  assert stages[-1]['result']==0 and stages[-2]['globals'][0]==0
  assert oracle.word(output)==dest+64*3*width
 for i in range(80):
  width,color,uv=rng.choice(formats);records=[vertex(width,[rng.uniform(-30,30) for _ in range(3)],uv) for _ in range(3)]
  case(width,records,bits(rng.choice([0,1,10,1e8])),color,uv,label='seeded three-dimensional geometry, color and UV interpolation')
 for word in [0,0x80000000,1,0x80000001,0x007fffff,0x00800000,bits(1e-20),bits(1e20),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
  for lane in range(3):
   records=[vertex(24,p,16) for p in [(0,0,0),(2,0,0),(0,2,0)]];struct.pack_into('<I',records[1],lane*4,word)
   case(24,records,bits(1),12,16,label='coordinate exponents, infinities and raw copied NaNs')
 for threshold in [0x80000000,1,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
  records=[vertex(24,p,16) for p in [(0,0,0),(2,0,0),(0,2,0)]]
  case(24,records,threshold,12,16,label='ordered threshold comparisons and NaNs')
 # The first emitted record overwrites the output-pointer word. It contains a
 # valid new destination, so later writes exercise the original reload order.
 records=[vertex(24,p,16) for p in [(0,0,0),(2,0,0),(0,2,0)]]
 struct.pack_into('<I',records[0],0,output+512)
 case(24,records,bits(float('inf')),12,16,extra=[[output,struct.pack('<I',output).hex()]],label='emitted vertex aliases output-pointer storage')
 assert all(branches[k] for k in ['empty','split','emit'])
 scope='Complete 4b8220 subdivision including its 1412-byte fall-through body. Empty, emit and split paths; all four child triangles and full three-level draining; valid 12..128-byte vertex formats, unaligned color/UV offsets, integer color rounding, PC24 area/midpoint arithmetic, numeric boundaries and output-pointer alias reloads. Full arena, 16 KB retained work stack and all six 128-byte scratch records compare. Capacity, three-record stack groups and fitting metadata offsets are caller contracts. No wall-mark rendering or playable scene is established.'
 fixture={'base':base,'memory':'decal-geometry-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
          'cases':oracle.cases,'case_labels':labels,'scope':scope,'branch_counts':dict(branches)}
 path=out/'decal-geometry-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
 print('Original decal geometry:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
 return fixture,path,oracle

if __name__=='__main__':
 from specimen import ROOT
 build_geometry(ROOT/'local/validation/collision')


def build_lifetime(out):
 import struct,json,random,subprocess,itertools
 from pathlib import Path
 from specimen import ROOT
 from script_heap_oracle import ScriptHeapOracle
 base,size=0x1800000,0x20000;context,manager,buffer=base+32,base+256,base+4096
 mem=bytearray(b'\xad'*size)
 struct.pack_into('<8I',mem,32,base+0x18000,base+size,0,base+0x10000,base,base+size,0,0)
 struct.pack_into('<I',mem,256+0x124,manager+0x200)
 functions={'0x490ec0':{'name':'thug_decal_advance_lifetime','this':False,'result':'void','cleanup':0,'memory':False,'stack_args':[1],'register_args':{'eax':0}}}
 globals_=[['thug_decal_reserved_slots',0x67dde0,4],['thug_decal_fade_step',0x67dde4,4]]
 oracle=ScriptHeapOracle(mem,base,context,manager,globals_,[128,8],functions,observe=[0x490ec0,0x4b7f30]);rng=random.Random(0x490ec0)
 def case(remaining,initial,elapsed,reserve=128,fade=8,alpha=None,repeats=1):
  data=bytearray(rng.getrandbits(8) for _ in range(0x7c10))
  struct.pack_into('<512I',data,0,*remaining,*initial)
  if alpha is not None:
   for i in range(256):
    for j,off in enumerate([0x1003+i*12,0x1007+i*12,0x100b+i*12,0x341f+i*72,0x3437+i*72,0x344f+i*72]):data[off]=alpha[j%len(alpha)]
  return oracle.case([(0x490ec0,0,[elapsed,buffer])]*repeats,[[buffer,data.hex()]],{0:reserve,1:fade})
 for elapsed in [0,1,2,99,100,101,0x7fffffff,0x80000000,0xffffffff]:
  for reserve in [0,1,128,255,256,257,0x80000000,0xffffffff]:
   case([100]*256,[200]*256,elapsed,reserve,repeats=2)
 for mode in range(6):
  for fade in [0,1,8,255,256,257,0x7fffffff,0x80000000,0xffffffff]:
   for alpha in [[0],[1],[255],[0,1,7,8,9,255]]:
    remaining=([0]*256 if mode==0 else [0xffffffff]*256 if mode==1 else [1]*256 if mode==2 else [100]*256)
    initial=([0]*256 if mode==3 else [100]*256 if mode==4 else [200]*256)
    case(remaining,initial,0,256,fade,alpha,repeats=3)
 for count in [0,1,127,128,129,255,256]:
  remaining=[100 if i<count else 0xffffffff for i in range(256)]
  initial=[200 if i%2 else 300 for i in range(256)]
  case(remaining,initial,1,128,8,alpha=[0],repeats=2)
 for _ in range(80):case([rng.getrandbits(32) for _ in range(256)],[rng.getrandbits(32) for _ in range(256)],rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32))
 fixture={'base':base,'memory':'decal-lifetime-memory.bin','globals':globals_,'functions':functions,'float_fields':[], 'cases':oracle.cases,'scope':'Complete 490ec0 lifetime and pressure-triggered fade update. Full 256-slot buffers, signed wrapping timers/ages, last-tie selection, selected-slot mutation during the same sweep, six alpha channels, delayed removal, repeated updates and negative timer sentinels compare exactly. Actual triangle-collapse callee executes; no engine or device substitute is used.'}
 directory=out;(directory/fixture['memory']).write_bytes(mem);(directory/'decal-lifetime-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
 print('Original decal lifetime',len(oracle.cases),sum(oracle.counts.values()),dict(oracle.coverage),flush=True)
 return fixture,directory/'decal-lifetime-fixtures.json',oracle


def build_lighting(out):
 import struct,json,random,subprocess,itertools
 from specimen import ROOT
 from script_heap_oracle import ScriptHeapOracle
 from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
 base,size=0x1800000,0x20000;context,manager,buffer=base+32,base+256,base+4096
 positions,source,output,normal=base+0x9000,base+0xa000,base+0xa400,base+0xa800
 mem=bytearray(b'\xad'*size)
 struct.pack_into('<8I',mem,32,base+0x18000,base+size,0,base+0x10000,base,base+size,0,0)
 struct.pack_into('<I',mem,256+0x124,manager+0x200)
 functions={'0x48f620':{'name':'thug_decal_light_colors','this':False,'result':'void','cleanup':0,'memory':False},'0x4b87b0':{'name':'thug_decal_refresh_colors','this':False,'result':'void','cleanup':0,'memory':False}}
 globals_=[['thug_decal_light_count',0x6faef4,4]]+[['thug_decal_lights',0x6faf80+i,4,i] for i in range(0,150*36,4)]
 oracle=ScriptHeapOracle(mem,base,context,manager,globals_,[0]+[0xadadadad]*(150*9),functions,observe=[0x48f620,0x4b87b0,0x48fa39,0x48f974,0x48fb33,0x48f67d,0x6236fc]);rng=random.Random(0x48f620)
 def patch(at,data):return [at,bytes(data).hex()]
 def light(pos=(0,0,0),intensity=1,radius=10,color=0x80706050):return struct.pack('<6f3I',*pos,1,intensity,radius,0xabcdef01,color,0)
 def case(lights=(),points=((0,0,0),(10,0,0),(11,0,0)),direction=None,shift=None,highest=None,extra=(),count=None,light_count=None):
  changes={0:(len(lights) if light_count is None else light_count)&0xffffffff}
  for j,data in enumerate(lights):
   for i,word in enumerate(struct.unpack('<9I',data)):changes[1+j*9+i]=word
  p=[patch(source,struct.pack('<16I',*[rng.getrandbits(32) for _ in range(16)])),patch(positions,b''.join(struct.pack('<4f',*xyz,1) for xyz in points))]
  if direction is not None:p.append(patch(normal,struct.pack('<3f',*direction)))
  fn=0x48f620;args=[source,output if shift is None else source+shift,positions,0 if direction is None else normal,len(points) if count is None else count]
  if highest is not None:
   fn=0x4b87b0;args=[buffer]
   data=bytearray(rng.getrandbits(8) for _ in range(0x7c10));struct.pack_into('<i',data,0x1c00,highest)
   for i in range(768):struct.pack_into('<3f',data,0x3410+i*24,(i//3)%10,0,0)
   p.append(patch(buffer,data))
  p.extend(extra)
  oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
  return oracle.case([(fn,0,args)],p,changes)
 for n in [0,1,2,3,4,5,7,8,9,149,150]:
  for direction in [None,(0,0,0),(1,0,0),(-1,0,0)]:
   lights=[light((i,0,0),intensity=(i%3)*.5) for i in range(n)]
   case(lights,direction=direction)
 for n in [0,1,3,4]:
  for shift in [None,-4,-3,-1,0,1,3,4,8]:
   case([light((i,0,0)) for i in range(n)],points=[(0,0,0),(10,0,0),(11,0,0),(5,0,0)],shift=shift)
 for word in [0,0x80000000,1,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
  for offset in [0,4,8,16,20]:
   record=bytearray(light());struct.pack_into('<I',record,offset,word)
   case([record],direction=(1,0,0))
 for i in range(100):
  lights=[light([rng.uniform(-20,20) for _ in range(3)],rng.uniform(0,2),rng.uniform(-30,30),rng.getrandbits(32)) for _ in range(rng.randrange(9))]
  points=[[rng.uniform(-10,10) for _ in range(3)] for _ in range(rng.randrange(1,6))]
  case(lights,points,None if i%2 else [rng.uniform(-1,1) for _ in range(3)])
 for n,highest in itertools.product([0,1,4],[-1,0,1,255]):case([light((i,0,0)) for i in range(n)],highest=highest)
 case(light_count=-1);case([light()],count=0)
 fixture={'base':base,'memory':'decal-lighting-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':'Complete 48f620 light selection/attenuation and 4b87b0 triangle color refresh. The original 150-light capacity, first-position selection of at most three lights, optional normal filtering, strict radius checks, x87 PC24 attenuation, RGB saturation, alpha preservation, empty-selection copy and unlit-output preservation compare exactly. Tests include overlapping colors, numeric boundaries, all 256 triangle slots and the real three-color wrapper callee.'}
 directory=out;(directory/fixture['memory']).write_bytes(mem);(directory/'decal-lighting-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
 print('Original decal lighting',len(oracle.cases),sum(oracle.counts.values()),dict(oracle.coverage),flush=True)
 return fixture,directory/'decal-lighting-fixtures.json',oracle
