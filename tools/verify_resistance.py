"""Slope turning and full drag/turn/friction chain against the original x86.

Only Windows last-error and TLS services are supplied; CRT math/error code runs.
"""
import hashlib,itertools,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'resistance.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'motion-fixtures.json').read_text());BASE=prior['base'];SIZE=0x20000
memory=bytearray((out/prior['memory']).read_bytes());rng=random.Random(0x506df0)
def alloc(size):
    at=BASE+len(memory);memory.extend(b'\xad'*size);assert len(memory)<SIZE;return at
def word(at):return struct.unpack_from('<I',memory,at-BASE)[0]
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def find(name):
    at=word(BASE+(name&4095)*4)
    while at and word(at+4)!=name:at=word(at+16)
    assert at;return at
def symbol(name,value):
    at=alloc(20);bucket=BASE+(name&4095)*4
    put(at,'<BBHIIII',0,2,0,name,0,bits(value),word(bucket));put(bucket,'<I',at);return at
physics=next(c['this'] for c in prior['cases'] if c['fn']=='0x4fe320');body=word(physics+12);state=word(physics+0x1528)
put(state+0x70,'<B',0);put(physics+0x350,'<f',0);put(physics+0x314,'<f',.5)
first=symbol(0xbed96eda,.0001);second=symbol(0x1a78b6fc,.0002)
skip=symbol(0x78f80ec4,0);rate=symbol(0x7dd5678b,1.5)
speed_limit=find(0x62a1fa03);slope_limit=find(0xc3527ef2)
# Append matching local numeric entries to exercise both parameter routes.
root=word(find(0x8cbc89dd)+12);local_members=[]
for name,value in [(0xbed96eda,.0003),(0x1a78b6fc,.0004),(0x78f80ec4,.5),(0x7dd5678b,2.5)]:
    member=alloc(16);put(member,'<4I',4,name,bits(value),word(root+4));put(root+4,'<I',member);local_members.append(member)
vectors=alloc(192);matrix=alloc(80)
initial=bytes(memory);(out/'resistance-memory.bin').write_bytes(initial)
STACK,STOP,OUTPUT,TLS=0x3000000,0x3f00000,0x2000600,0x2000800
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(0x2000000,0x10000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
for _,at,value in prior['globals']:cpu.mem_write(at,struct.pack('<I',value))
cpu.mem_write(0x684fe4,struct.pack('<I',0x5df4ac))
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
# The original CRT's initialized TLS slot plus GetLastError/SetLastError services.
# No THUG2 math, script, movement or CRT function is replaced by a hook.
GET_ERROR,GET_TLS,SET_ERROR=STOP+0x100,STOP+0x110,STOP+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:cpu.mem_write(slot,struct.pack('<I',target))
cpu.mem_write(0x68ef14,struct.pack('<I',7))
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
last_error=0x12345678;os_calls=Counter()
def os_service(uc,address,size,user):
    global last_error
    sp=uc.reg_read(UC_X86_REG_ESP)
    if address==GET_ERROR:uc.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
    elif address==GET_TLS:
        assert struct.unpack('<I',uc.mem_read(sp+4,4))[0]==7
        uc.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
    else:last_error=struct.unpack('<I',uc.mem_read(sp+4,4))[0];os_calls['SetLastError']+=1
for address in [GET_ERROR,GET_TLS,SET_ERROR]:cpu.hook_add(UC_HOOK_CODE,os_service,begin=address,end=address)
functions={
    '0x406080':{'name':'thug_vector_project_plane','result':'word','cleanup':4},
    '0x406630':{'name':'thug_vector_signed_angle','result':'double','cleanup':0,'this':False,'double_ulp_limit':1},
    '0x404e20':{'name':'thug_matrix_rotation_y','result':'word','cleanup':0,'this':False,'float_args':[1]},
    '0x501b00':{'name':'thug_skater_slope_turn','result':'byte','cleanup':0},
    '0x506df0':{'name':'thug_skater_apply_resistance','result':'void','cleanup':0}}
cases=[];counts=Counter();coverage=Counter();events=Counter();acos_inputs=[]
def observe(uc,address,size,user):events[hex(address)]+=1;coverage[hex(address)]+=1
for address in [0x406080,0x406630,0x404e20,0x501b00,0x4fe6a0,0x4fe730,0x580400,0x623630,0x62bc7d,0x5df4ac]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
def observe_acos(uc,address,size,user):
    acos_inputs.append(bytes(uc.mem_read(uc.reg_read(UC_X86_REG_ESP),8)).hex())
cpu.hook_add(UC_HOOK_CODE,observe_acos,begin=0x623636,end=0x623636)
def run(fn,this=physics,args=(),patches=(),writes=()):
    global last_error
    info=functions[hex(fn)];expected=bytearray(initial)
    for at,data in patches:expected[at-BASE:at-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x7ce4fd,b'\xad');cpu.mem_write(0,struct.pack('<I',0xa5a5a5a5))
    cpu.mem_write(TLS,bytes(0x100));cpu.mem_write(TLS+8,struct.pack('<i',-123));last_error=0x12345678
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP+32 if info['result']=='double' else STOP,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    events.clear();acos_inputs.clear();cpu.emu_start(fn,STOP,count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+info['cleanup'],hex(fn)
    assert cpu.reg_read(UC_X86_REG_FPCW)==0x7f and last_error==0x12345678
    assert bytes(cpu.mem_read(0,4))==struct.pack('<I',0xa5a5a5a5)
    after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
    for at,length in writes:
        data=after[at-BASE:at-BASE+length];expected[at-BASE:at-BASE+length]=data;outputs.append([at,data.hex()])
    assert after==expected,('unexpected write',hex(fn))
    result=bytes(cpu.mem_read(OUTPUT,8)).hex() if info['result']=='double' else cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff) if info['result']!='void' else None
    cases.append({'fn':hex(fn),'this':this,'args':list(args),'patches':list(patches),'outputs':outputs,'result':result,
        'flag':cpu.mem_read(0x7ce4fd,1)[0],'errno':struct.unpack('<i',cpu.mem_read(TLS+8,4))[0],'events':dict(events),'acos_inputs':list(acos_inputs)})
    counts[info['name']]+=1

special=[[0,0,0,1],[1,0,0,0],[-1,0,0,7],[0,1,0,1],[0,0,1,1],
    [1e-30,-1e-30,1e-30,1],[1e30,2e30,3e30,0],[float('nan'),1,2,1],[float('inf'),1,0,1]]
for i in range(512):
    value=special[i%len(special)] if i<72 else [rng.uniform(-20,20) for _ in range(4)]
    normal=[rng.uniform(-2,2) for _ in range(4)]
    for offset in [-8,0,4,16]:
        p=[patch(vectors+64,'<4f',*value),patch(vectors+64+offset,'<4f',*normal)]
        run(0x406080,this=vectors+64,args=[vectors+64+offset],patches=p,writes=[(vectors+64,16)])
for i in range(1024):
    a=special[i%len(special)] if i<81 else [rng.uniform(-1000,1000) for _ in range(4)]
    b=special[(i//len(special))%len(special)] if i<81 else [rng.uniform(-1000,1000) for _ in range(4)]
    n=[0,1,0,0] if i%3==0 else [rng.uniform(-10,10) for _ in range(4)]
    p=[patch(vectors,'<12f',*a,*b,*n)]
    run(0x406630,args=[vectors,vectors+16,vectors+32],patches=p)
angles=[0.,-0.,1e-30,1e-5,math.pi/2,math.pi,-math.pi,1e6,float('nan')]+[rng.uniform(-50,50) for _ in range(247)]
for angle in angles:run(0x404e20,args=[matrix,bits(angle)],writes=[(matrix,64)])

identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
def world(i):
    tilt=rng.choice([0,.1,.25,.5,1.,-1.]);s=math.sqrt(max(0,1-tilt*tilt))
    orient=[1,0,0,0,0,tilt,s,0,0,-s,tilt,0,1,2,3,1]
    velocity=rng.choice([[0,0,0,1],[.0009999,0,0,7],[.001,0,0,1],[.0010001,0,0,0],
        [10,0,0,1],[0,-10,0,1],[0,0,10,1],[20,20,-5,1],[100,0,200,1],[float('nan'),0,10,1]])
    p=[patch(body+0x6c,'<16f',*orient),patch(physics+0x18,'<16f',*(identity if i%2 else orient)),
        patch(physics+0x68,'<4f',0,tilt,s,0),patch(body+0xac,'<4f',*velocity),
        patch(physics+0x8c,'<f',rng.choice([0,1/60,1/30,-1/60,.5,1.,float('nan')])),
        patch(body+0xbc,'<B',1),patch(physics+0x302,'<B',i%2),patch(physics+0x2d9,'<B',i&1),
        patch(state+0x70,'<B',(i>>1)&1),patch(state+0x20,'<B',(i>>2)&1),
        patch(physics+0x314,'<f',rng.choice([0,.5,1.,100.,-1.,float('nan')])),
        patch(speed_limit+12,'<f',rng.choice([0,25,100,500,float('nan')])),
        patch(slope_limit+12,'<f',rng.choice([0,.25,.5,1.,float('nan')])),
        patch(rate+1,'<B',1 if i%5==0 else 2),patch(rate+12,'<I',2**24+1 if i%5==0 else bits(rng.choice([0,1.,-1.,5.])))]
    if i%7==0:p += [patch(physics+0x350,'<f',float('nan') if i%14 else 1),patch(physics+0x35c,'<f',rng.choice([0.,.0003,-.0003]))]
    return p
for i in range(1536):
    p=world(i)
    run(0x501b00,patches=p,writes=[(body+0x6c,64),(physics+0x18,64)])
    run(0x506df0,patches=p,writes=[(body+0x6c,80),(physics+0x18,64)])
assert coverage['0x4fe730'] and coverage['0x623630'] and coverage['0x62bc7d'] and coverage['0x5df4ac']
scope='Complete resistance chain: configured drag, slope turning and friction; signed-angle CRT runs with modeled Windows TLS/error services. Standalone angle allows one double ULP with identical float rounding; parent writes remain exact except NaN classification. Constructed states, no full skating update.'
fixture={'base':BASE,'memory':'resistance-memory.bin','globals':prior['globals'],'functions':functions,'cases':cases,
    'float_ranges':[[body+0x6c,80],[physics+0x18,64],[vectors,192],[matrix,64]],'coverage':dict(coverage),'scope':scope}
path=out/'resistance-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',dict(counts),'OS services',dict(os_calls),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_resistance_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'os_services':dict(os_calls),
    'x87_control_word':'0x007f','mxcsr':'0x1f80','scope':scope,
    'transcendental_limit':'Unicorn FPATAN uses host atan2; SDK atan2 can differ by one double ULP. Signed-angle comparison requires identical float rounding and bounds/reports every double difference. All complete parent-state comparisons remain exact except NaN classification.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'resistance-memory.bin']},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
