"""Original D3DX projection math with explicitly pinned emulator seed semantics."""
import struct,json,random
from script_heap_oracle import ScriptHeapOracle
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR

def build_math(directory):
    base,size=0x1800000,0x10000;context,manager=base+32,base+256
    out,inp,mat,eye,target,up=[base+x for x in [0x1000,0x2000,0x3000,0x4000,0x4100,0x4200]]
    mem=bytearray(b'\xad'*size)
    struct.pack_into('<8I',mem,32,base+0x8000,base+size,0,base+0x7000,base,base+size,0,0)
    struct.pack_into('<I',mem,256+0x124,manager+0x200)
    functions={}
    for at,name,n in [(0x5e17ed,'thug_d3dx_normalize3_sse',2),(0x5e16ea,'thug_d3dx_transform_coordinate_sse',3),(0x5c0985,'thug_d3dx_look_at_rh',4),(0x5c0b39,'thug_d3dx_ortho_rh',5)]:functions[hex(at)]={'name':name,'this':False,'result':'word','cleanup':n*4,'memory':False}
    functions['0x5c0b39']['float_args']=[1,2,3,4]
    oracle=ScriptHeapOracle(mem,base,context,manager,[],[],functions,observe=[int(k,16) for k in functions]+[0x5bef2d])
    oracle.setword(0x684ff4,0x5e17ed)
    rng=random.Random(0x5e17ed)
    def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
    def patch(at,words):return [at,struct.pack('<'+'I'*len(words),*words).hex()]
    def case(fn,args,p=()):
     oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
     stages=oracle.case([(fn,0,args)],p)
     for s in stages:s['float_fields']=[args[0]+i*4 for i in range(16 if fn in [0x5c0985,0x5c0b39] else 3)]
     return stages
    special=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,bits(1e-8),bits(2**-23),bits(2**-23)-1,bits(2**-23)+1,bits(1),bits(1e20),0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
    identity=[bits(float(i//4==i%4)) for i in range(16)]
    for word in special:
     for lane in range(3):
      values=[0,0,0];values[lane]=word
      case(0x5e17ed,[out,inp],[patch(inp,values)])
    for i in range(200):
     values=[bits(rng.uniform(-100,100)) for _ in range(3)] if i<150 else [rng.getrandbits(32) for _ in range(3)]
     dest=inp+rng.randrange(-11,12) if i%2 else out
     case(0x5e17ed,[dest,inp],[patch(inp,values)])
    for i in range(250):
     values=[bits(rng.uniform(-100,100)) for _ in range(3)];m=[bits(rng.uniform(-10,10)) for _ in range(16)]
     if i<50:m=identity[:];m[rng.randrange(16)]=rng.choice(special)
     address=mat+i%16;dest=address+rng.randrange(64) if i%3==0 else inp+rng.randrange(-11,12) if i%3==1 else out
     case(0x5e16ea,[dest,inp,address],[patch(inp,values),patch(address,m)])
    for word in special:
     for lane in range(4):
      values=[bits(2),bits(3),bits(.1),bits(100)];values[lane]=word
      case(0x5c0b39,[out,*values])
    for i in range(160):
     case(0x5c0b39,[out,*[rng.getrandbits(32) for _ in range(4)]])
    for i in range(180):
     values=[[bits(rng.uniform(-10,10)) for _ in range(3)] for _ in range(3)]
     if i<50:values[i%3][(i//3)%3]=rng.choice(special)
     dest=[out,eye,target,up][i%4]+(i//4)%16
     case(0x5c0985,[dest,eye,target,up],[patch(eye,values[0]),patch(target,values[1]),patch(up,values[2])])
    # Degenerate view frames and reciprocal-depth boundaries are separate from
    # random coverage; they exercise zero, parallel and tiny homogeneous axes.
    for e,t,u in [((0,0,0),(0,0,0),(0,1,0)),((0,0,1),(0,0,0),(0,0,1)),
                  ((0,0,1),(0,0,0),(0,0,-1)),((0,0,1),(0,0,0),(0,0,0)),
                  ((0,0,1),(0,0,0),(0,1,0)),((1,0,0),(0,0,0),(0,1,0))]:
     for dest in [out,eye,target,up]:
      case(0x5c0985,[dest,eye,target,up],[patch(eye,[bits(x) for x in e]),patch(target,[bits(x) for x in t]),patch(up,[bits(x) for x in u])])
    for word in special:
     for alignment in [0,1,4,15]:
      m=identity[:];m[15]=word;address=mat+alignment
      case(0x5e16ea,[out,inp,address],[patch(inp,[bits(1),bits(2),bits(3)]),patch(address,m)])
    
    fixture={"base":base,"memory":"decal-math-memory.bin","globals":[],"functions":functions,"float_fields":[],"cases":oracle.cases,"scope":'Four complete D3DX routines: selected SSE normalization and coordinate transform, right-handed look-at and orthographic matrices. Seed adapters deliberately follow Unicorn 2.1.4 float32 division/sqrt; physical Intel/AMD approximation tables are not reproduced. Actual normalize dispatch executes inside look-at. Preserves aliases, alignment paths, cutoff, zero/parallel axes and wide PC24 depth/translation arithmetic. Typed computed NaNs compare by classification; all other results and arena bytes are exact.'}
    (directory/fixture["memory"]).write_bytes(mem)
    path=directory/"decal-math-fixtures.json"
    path.write_text(json.dumps(fixture,separators=(",",":")))
    print("Original decal math:",len(oracle.cases),sum(oracle.counts.values()),flush=True)
    return fixture,path,oracle
