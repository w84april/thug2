"""Original skater drag, friction, obstacle queries, and probe constructors."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'skater.json';report_path.unlink(missing_ok=True)
base=json.loads((out/'loading-fixtures.json').read_text())['datasets'][0]
moving=json.loads((out/'moving-fixtures.json').read_text());geometry=json.loads((out/'geometry-fixtures.json').read_text())
vertices,normals=[(out/f).read_bytes() for f in ['vertices.bin','normals.bin']]
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=0x1000000,0x1200000,0x1400000,0x1402000,0x1500000,0x1501000,0x1502000,0x1503000
BODY,PHYSICS,SYMBOLS,PARAMS=0x1600000,0x1610000,0x1900000,0x1904100
PROBE,VECTOR,POINTS,STATE,HEAP=0x2000c00,0x2000600,0x2000800,0x2000500,0x2400000
STACK,STOP,QUERY_STATE,STAMP=0x3000000,0x3f00000,0x691968,0x693998
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes())
heap=(out/base['heap']).read_bytes();rng=random.Random(0x4fe730);counts=Counter()
fixture={'addresses':{'data':DATA,'grid':GRID,'scene':SCENE,'scenes':SCENES,'runtime':RUNTIME,'nodes':NODES,'owners':OWNERS,'refs':REFS,
    'body':BODY,'physics':PHYSICS,'symbols':SYMBOLS,'params':PARAMS,'probe':PROBE,'vector':VECTOR,'points':POINTS,'state':STATE,'heap':HEAP},
    'loader':base,'constructors':[],'vectors':[],'velocity':[],'world':[]}

def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def floats(values):return struct.pack('<'+'f'*len(values),*values)
def word(at):return struct.unpack('<I',raw(at,4))[0]
def fbits(n):return struct.unpack('<I',struct.pack('<f',n))[0]

def call(fn,this,args=(),cleanup=0):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    return cpu.reg_read(UC_X86_REG_EAX)

for i in range(192):
    initial=bytes(rng.randrange(256) for _ in range(176));points=bytes(rng.randrange(256) for _ in range(32))
    cpu.mem_write(PROBE,initial+b'\xad'*16);cpu.mem_write(POINTS,points)
    kind=['default','points','set'][i%3]
    fn={'default':0x417760,'points':0x417250,'set':0x4171d0}[kind]
    returned=call(fn,PROBE,[] if kind=='default' else [POINTS,POINTS+16],0 if kind=='default' else 8)
    if kind!='set':assert returned==PROBE
    assert raw(PROBE+176,16)==b'\xad'*16 and raw(POINTS,32)==points
    fixture['constructors'].append({'kind':kind,'initial':initial.hex(),'points':points.hex(),'output':raw(PROBE,176).hex()})

vectors=[[0,0,0,1],[-0.,0,-0.,-0.],[1,2,3,7],[float('nan'),1,2,1],[float('inf'),1,2,1]]
vectors += [[rng.uniform(-1e4,1e4) for _ in range(4)] for _ in range(512)]
for i,vector in enumerate(vectors):
    length=[0,-1,1,1e-4,100][i%5];source=floats(vector);cpu.mem_write(VECTOR,source+b'\xad'*16)
    assert call(0x42bbf0,VECTOR,[fbits(length)],4)==VECTOR
    assert raw(VECTOR+16,16)==b'\xad'*16
    fixture['vectors'].append({'input':source.hex(),'length':length,'output':raw(VECTOR,16).hex()})

math_cases=[(v,dt,friction) for v in [[0,0,0,1],[1e-4,0,0,1],[.001,0,0,1],[1,0,0,1],[3,4,0,1],[float('nan'),1,2,1],[float('inf'),1,2,1]] for dt,friction in [(0,1),(1/60,0),(1/60,1),(1,100),(-1/60,1)]]
for i in range(2048):
    scale=10**rng.uniform(-6,4);v=[rng.uniform(-1,1)*scale for _ in range(3)]+[rng.choice([0,1,-1,7])]
    math_cases.append((v,rng.choice([1/30,1/60,1/144,0,-1/60]),rng.choice([0,1e-6,.0001,.01,1,100,-.01])))
for kind,fn in [('drag',0x4fe1f0),('friction',0x4fe730)]:
    for vector,dt,coefficient in math_cases:
        body=bytearray(b'\xad'*0xbc);body[0xac:0xbc]=floats(vector)
        physics=bytearray(b'\xad'*0x318);struct.pack_into('<I',physics,12,BODY);struct.pack_into('<f',physics,0x8c,dt);struct.pack_into('<f',physics,0x314,coefficient)
        cpu.mem_write(BODY,bytes(body)+b'\xad'*16);cpu.mem_write(PHYSICS,bytes(physics)+b'\xad'*16)
        call(fn,PHYSICS,[fbits(coefficient)] if kind=='drag' else [],4 if kind=='drag' else 0)
        assert raw(BODY,0xac)==body[:0xac] and raw(BODY+0xbc,16)==b'\xad'*16
        assert raw(PHYSICS,0x328)==bytes(physics)+b'\xad'*16
        fixture['velocity'].append({'kind':kind,'input':floats(vector).hex(),'time_step':dt,'coefficient':coefficient,'output':raw(BODY+0xac,16).hex()})
        counts[kind]+=1

cpu.mem_write(SCENE,b'\0'*0xd4+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0);put(0x6f3624,'<I',SYMBOLS)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
references=bytearray(48);owners=bytearray(96)
for j in range(3):
    struct.pack_into('<3I',references,j*16,OWNERS+j*32,0,0)
    struct.pack_into('<8I',owners,j*32,0,REFS+j*16,0,0,0,0xabc000+j,0,0)
fixture['owners']=owners.hex();fixture['references']=references.hex()
# Parameter variant: empty/default; unnamed float; alias to an integer symbol.
script=bytearray(0x4200);struct.pack_into('<I',script,0x321*4,SYMBOLS+0x4000)
struct.pack_into('<BBHIIII',script,0x4000,0,1,0,0xbcdef321,0,30,0)
fixture['script_memory']=script.hex();cpu.mem_write(SYMBOLS,bytes(script))
for index,(obj,helper) in enumerate(zip(geometry['objects'],moving['helpers'])):
    if obj['faces']:
        record=word(DATA+obj['object']+12);small=raw(DATA+obj['object']+10,1)[0]
        indices=struct.unpack('<3B' if small else '<3H',raw(record+4,3 if small else 6))
        points=[struct.unpack_from('<3f',vertices,obj['vertex_start']+i*16) for i in indices]
        center=[sum(p[i] for p in points)/3 for i in range(3)];normal=struct.unpack_from('<3f',normals,obj['normal_start'])
    else:center=[0,0,0];normal=[0,1,0]
    side=[normal[2],0,-normal[0]];length=math.sqrt(sum(v*v for v in side));side=[v/length for v in side] if length else [1,0,0]
    for variant in range(3):
        cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes(owners));cpu.mem_write(REFS,bytes(references));cpu.mem_write(RUNTIME,b'\xad'*0x300)
        for j in range(3):
            actor=RUNTIME+j*0x100;cpu.mem_write(actor,bytes.fromhex(helper['initialized']));put(actor+0xa0,'<I',OWNERS+j*32)
            put(actor+0x10,'<4f',*[normal[i]*(j-1)*4 for i in range(3)],1)
            put(actor+8,'<H',2 if variant==1 and j==1 else 0)
        actors=raw(RUNTIME,0x300)
        body=bytearray(b'\xad'*0xbc);distance=[8,4,40][variant]
        struct.pack_into('<4f',body,0x4c,*[center[i]+normal[i]*distance for i in range(3)],1)
        struct.pack_into('<16f',body,0x6c,*side,0,0,1,0,0,*[-v for v in normal],0,0,0,0,1)
        physics=bytearray(b'\xad'*0x318);struct.pack_into('<I',physics,12,BODY)
        cpu.mem_write(BODY,bytes(body)+b'\xad'*16);cpu.mem_write(PHYSICS,bytes(physics)+b'\xad'*16)
        params=struct.pack('<2I',0,SYMBOLS+0x4110 if variant else 0)
        component=struct.pack('<4I',4 if variant==1 else 26,0,fbits(10) if variant==1 else 0xbcdef321,0)
        cpu.mem_write(PARAMS,params+bytes(8)+component)
        state=struct.pack('<3I',0x12345678,0xabcdef01,0x13579bdf);cpu.mem_write(QUERY_STATE,state)
        stamp=(index*3+variant)&255;cpu.mem_write(STAMP,bytes([stamp]));cpu.mem_write(0x691910,b'\0')
        call(0x5009c0,PHYSICS)
        direction=word(PHYSICS+0x2d4)
        returned=call(0x4fd660,PHYSICS,[PARAMS,0xdeadbeef],8)
        assert returned in (0,1) and word(0)==0
        assert raw(BODY,0xcc)==bytes(body)+b'\xad'*16 and raw(PHYSICS+0x318,16)==b'\xad'*16
        assert raw(OWNERS,96)==owners and raw(REFS,48)==references,'Temporary moving reference leaked'
        fixture['world'].append({'object':obj['object'],'actors':actors.hex(),'actors_after':raw(RUNTIME,0x300).hex(),
            'body':bytes(body).hex(),'physics':bytes(physics).hex(),'physics_after':raw(PHYSICS,0x318).hex(),
            'params':(params+bytes(8)+component).hex(),'initial_state':state.hex(),'state':raw(QUERY_STATE,12).hex(),
            'stamp':stamp,'final_stamp':raw(STAMP,1)[0],'direction':direction,'returned':returned,
            'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex()})
        counts['nearby_queries']+=1;counts['forward_queries']+=1;counts['directions_found']+=int(direction!=0);counts['forward_hits']+=returned
    if index%100==0:print(index,'objects',dict(counts),flush=True)
path=out/'skater-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_skater_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'probe_helpers':len(fixture['constructors']),'vector_length_cases':len(fixture['vectors']),
    'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'scope':'Original skater friction/drag and nearby/forward obstacle queries on loader-built training collision with constructed body states and moving objects; no complete movement update or QB loader.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()},'byte_matching':'not attempted'}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':'pass','counts':dict(counts)},indent=2))
