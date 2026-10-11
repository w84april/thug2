"""Recover the full skater surface query and check its classification boundary.

The suffix checks enter the original 0x5003f3 instructions with the stack/registers
they have after a successful probe. Full-query cases also execute the actual probe.
No game instructions or math calls are replaced in the x86 oracle.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_ESI,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'surface.json';report_path.unlink(missing_ok=True)
previous=json.loads((out/'skater-fixtures.json').read_text());a=previous['addresses'];base=previous['loader']
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=[a[k] for k in ('data','grid','scene','scenes','runtime','nodes','owners','refs')]
BODY,PHYSICS,SYMBOLS,PROBE,HEAP=[a[k] for k in ('body','physics','symbols','probe','heap')]
STACK,STOP,QUERY_STATE,STAMP,OUT=0x3000000,0x3f00000,0x691968,0x693998,0x2001000
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x5003a0);counts=Counter()
fixture={'addresses':a,'loader':base,'globals':[],'flags':[],'classifications':[],'world':[],
    'owners':previous['owners'],'references':previous['references'],
    'oracle_limitations':{'unicorn_fsin':'Unicorn 2.1.4 uses host double sin and leaves infinity unchanged. It does not independently validate hardware FSIN precision.',
        'source':'https://github.com/unicorn-engine/unicorn/blob/2.1.4/qemu/target/i386/fpu_helper.c#L910',
        'intel_fsin':'https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf'}}
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def fbits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def frombits(x):return struct.unpack('<f',struct.pack('<I',x))[0]
def call(fn,this,args=(),cleanup=0,numeric=False):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP+32 if numeric else STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    return cpu.reg_read(UC_X86_REG_EAX)&255
# Capture ST(0) as double without invoking any Windows runtime.
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUT)+b'\xe9'+struct.pack('<i',-43))
script=bytearray(0x4100)
NAME=0x3eede4d3;ENTRY=SYMBOLS+0x4000
struct.pack_into('<I',script,(NAME&4095)*4,ENTRY)
struct.pack_into('<BBHIIII',script,0x4000,0,2,0,NAME,0,fbits(30),0)
cpu.mem_write(SYMBOLS,bytes(script));put(0x6f3624,'<I',SYMBOLS)
fixture['script_memory']=script.hex()
def symbol(kind,value):
    cpu.mem_write(ENTRY+1,bytes([kind]));put(ENTRY+12,'<I',value)

values=[0,1,0x80000000,0x7fffffff,0xffffffff,16777217,16777219,0x7f800000,0xff800000,0x7fc12345,0x80000001]
values += [rng.randrange(2**32) for _ in range(512)]
for kind in [0,1,2,10,13]:
    for value in values:
        symbol(kind,value)
        call(0x478f00,0,[NAME,1],numeric=True)
        fixture['globals'].append({'type':kind,'value':value,'output':raw(OUT,8).hex()})
for i in range(256):
    initial=bytes(rng.randrange(256) for _ in range(176));cpu.mem_write(PROBE,initial+b'\xad'*16)
    excluded=rng.randrange(2**32);required=rng.randrange(2**32)
    call(0x4170f0,PROBE,[excluded,required],8)
    assert raw(PROBE+176,16)==b'\xad'*16
    fixture['flags'].append({'initial':initial.hex(),'excluded':excluded,'required':required,'output':raw(PROBE,176).hex()})

def classify(flags,angle_type,angle_bits,normal_bits,checksum=1,flag40=0):
    symbol(angle_type,angle_bits)
    initial=bytearray(b'\xad'*0x318)
    struct.pack_into('<H',initial,0xf8,flags);struct.pack_into('<I',initial,0x100,checksum)
    initial[0x115]=flag40;struct.pack_into('<I',initial,0x134,normal_bits)
    cpu.mem_write(PHYSICS,bytes(initial)+b'\xad'*16)
    sp=STACK+0x18000;cpu.mem_write(sp,bytes(40));put(sp+0x1c,'<I',STOP);cpu.mem_write(sp+0x24,b'\x01')
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ESI,PHYSICS);cpu.reg_write(UC_X86_REG_EBX,0);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(0x5003f3,STOP,count=100000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+40
    result=raw(PHYSICS,0x318);expected=initial[:]
    expected[0x104:0x108]=result[0x104:0x108];expected[0x228:0x22b]=result[0x228:0x22b]
    assert result==expected and raw(PHYSICS+0x318,16)==b'\xad'*16
    test={'flags':flags,'type':angle_type,'angle':angle_bits,'normal':normal_bits,
        'checksum':checksum,'flag40':flag40,'cleared':result[0x104:0x108].hex(),'output':result[0x228:0x22b].hex()}
    if not (flags&15) and angle_type==2 and math.isinf(frombits(angle_bits)):
        # Retain the unmodified oracle output. Intel specifies invalid-operation
        # for FSIN(infinity); with the game's masked exceptions this produces
        # NaN and its unordered comparison accepts the surface.
        test['documented_processor_output']='010000'
        counts['infinity_specification_checks']+=1
        counts['documented_oracle_differences']+=int(test['output']!='010000')
    fixture['classifications'].append(test)
for flags in list(range(256))+[0x4000,0x8000,0xffff]:
    for checksum,flag40 in [(0,0),(1,0),(0,1),(1,1)]:
        classify(flags,2,fbits(30),fbits(.4),checksum,flag40)
# Adjacent representable float normals around each sine. The original compares
# extended sine directly to a float normal; rounding sine first is incorrect.
angles=[i/4 for i in range(-1440,1441)]+[-1e-40,1e-40,-1e8,1e8,-0.,float('inf'),float('-inf'),float('nan')]
for angle in angles:
    radians=frombits(fbits(frombits(fbits(angle))*frombits(fbits(math.pi/180))))
    threshold=math.sin(radians) if math.isfinite(radians) else float('nan')
    bits=fbits(threshold)
    normals=[bits,fbits(-1),fbits(0),fbits(1),0x7fc12345]
    if math.isfinite(threshold) and threshold!=0:normals.extend([bits-1,bits+1])
    for normal in normals:classify(0,2,fbits(angle),normal)
for value in [0,1,30,90,180,0x7fffffff,0x80000000,16777217,0xffffffff,15988707,31977414,260835357,521670714]:
    for normal in [-1,-.5,0,.5,1]:classify(0,1,value,fbits(normal))
print('Classification cases:',len(fixture['classifications']),flush=True)

cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes())
heap=(out/base['heap']).read_bytes()
cpu.mem_write(SCENE,b'\0'*0xd4+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
for index,test in enumerate(previous['world']):
    cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes.fromhex(previous['owners']));cpu.mem_write(REFS,bytes.fromhex(previous['references']))
    cpu.mem_write(RUNTIME,bytes.fromhex(test['actors']));cpu.mem_write(BODY,bytes.fromhex(test['body']))
    cpu.mem_write(PHYSICS,bytes.fromhex(test['physics'])+b'\xad'*16)
    call(0x417760,PHYSICS+0xa8)
    # Include a previous attachment to check replacement/unlinking by the probe.
    if index%2:
        put(PHYSICS+0x140,'<3I',OWNERS,0,REFS)
        put(REFS+4,'<I',PHYSICS+0x140);put(OWNERS+4,'<I',PHYSICS+0x140)
    body=bytes.fromhex(test['body']);position=struct.unpack_from('<4f',body,0x4c);axis=struct.unpack_from('<4f',body,0x8c)
    distance=[16,80,0][index%3]
    segment=struct.pack('<8f',*position,*[position[i]+axis[i]*distance for i in range(3)],position[3])
    cpu.mem_write(PHYSICS+0x208,segment)
    initial=raw(PHYSICS,0x318);owners_before=raw(OWNERS,96);refs_before=raw(REFS,48)
    excluded,required=[(0x10,0),(0,0),(0xffff,0),(0,8),(0,1)][index%5]
    angle=[0,15,30,45,60,90][index%6];symbol(2,fbits(angle))
    cpu.mem_write(QUERY_STATE,bytes.fromhex(test['initial_state']));cpu.mem_write(STAMP,bytes([test['stamp']]));cpu.mem_write(0x691910,b'\0')
    returned=call(0x5003a0,PHYSICS,[excluded,required],8)
    assert returned in (0,1) and raw(PHYSICS+0x318,16)==b'\xad'*16
    assert raw(BODY,0xbc)==body
    fixture['world'].append({'actors':test['actors'],'actors_after':raw(RUNTIME,0x300).hex(),'body':test['body'],
        'physics':initial.hex(),'physics_after':raw(PHYSICS,0x318).hex(),'excluded':excluded,'required':required,'angle':angle,
        'owners':owners_before.hex(),'owners_after':raw(OWNERS,96).hex(),'references':refs_before.hex(),'references_after':raw(REFS,48).hex(),
        'initial_state':test['initial_state'],'state':raw(QUERY_STATE,12).hex(),'stamp':test['stamp'],'final_stamp':raw(STAMP,1)[0],
        'returned':returned,'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex()})
    counts['queries']+=1;counts['hits']+=returned
    if returned:counts['skatable']+=raw(PHYSICS+0x228,1)[0];counts['flag_8']+=raw(PHYSICS+0x229,1)[0];counts['flag_4']+=raw(PHYSICS+0x22a,1)[0]
    if index%300==0:print(index,'surface queries',dict(counts),flush=True)
path=out/'surface-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_surface_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'numeric_getters':len(fixture['globals']),
    'flag_setters':len(fixture['flags']),'classifications':len(fixture['classifications']),
    'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'oracle_limitations':fixture['oracle_limitations'],
    'scope':'Full surface query on training collision and constructed moving objects; classification suffix checked at float boundaries with SDK sine adapter, not full x87 transcendental emulation.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts'],indent=2))
