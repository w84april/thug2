"""Wall-tangent turning and the game's heading approximation against x86.

The CRT math code executes; only Windows TLS and last-error services are modeled.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'wall-turn.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x10000;memory=bytearray(0x4000);rng=random.Random(0x5039f0)
def alloc(size):
 at=BASE+len(memory);memory.extend(b'\xad'*size);assert len(memory)<SIZE;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def frombits(value):return struct.unpack('<f',struct.pack('<I',value))[0]
rate=alloc(20);put(rate,'<BBHIIII',0,2,0,0xe07ee1a9,0,bits(1.5),0);put(BASE+(0xe07ee1a9&4095)*4,'<I',rate)
body=alloc(0x2a0);physics=alloc(0x1540);vectors=alloc(128);turn=alloc(16);put(physics+12,'<I',body)
prior={'globals':[['thug_script_symbol_buckets',0x6f3624,BASE]]}
initial=bytes(memory);(out/'wall-turn-memory.bin').write_bytes(initial)
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
 '0x403ef0':{'name':'thug_acos_approximate','result':'double','cleanup':0,'this':False,'float_args':[0]},
 '0x5039f0':{'name':'thug_skater_wall_turn','result':'double','cleanup':12,'float_args':[2]}}
cases=[];counts=Counter();coverage=Counter();events=Counter();acos_inputs=[];matrix_infinity_calls=[]
def observe(uc,address,size,user):events[hex(address)]+=1;coverage[hex(address)]+=1
for address in [0x478f00,0x623630,0x62bc7d,0x404e20,0x5df4ac]:
 cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
def observe_acos(uc,address,size,user):
 acos_inputs.append(bytes(uc.mem_read(uc.reg_read(UC_X86_REG_ESP),8)).hex())
cpu.hook_add(UC_HOOK_CODE,observe_acos,begin=0x623636,end=0x623636)
def observe_matrix(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP)
    caller=struct.unpack('<I',uc.mem_read(sp,4))[0]
    angle_bits=struct.unpack('<I',uc.mem_read(sp+8,4))[0]
    assert caller in (0x503ac1,0x503ae2)
    if math.isinf(frombits(angle_bits)):
        target=body+0x6c if caller==0x503ac1 else physics+0x18
        matrix_infinity_calls.append({'caller':hex(caller),'angle_bits':angle_bits,'target':target})
cpu.hook_add(UC_HOOK_CODE,observe_matrix,begin=0x404e20,end=0x404e20)
def run(fn,this=physics,args=(),patches=(),writes=()):
    global last_error
    info=functions[hex(fn)];expected=bytearray(initial)
    for at,data in patches:expected[at-BASE:at-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x7ce4fd,b'\xad');cpu.mem_write(0,struct.pack('<I',0xa5a5a5a5))
    cpu.mem_write(TLS,bytes(0x100));cpu.mem_write(TLS+8,struct.pack('<i',-123));last_error=0x12345678
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP+32 if info['result']=='double' else STOP,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    events.clear();acos_inputs.clear();matrix_infinity_calls.clear();cpu.emu_start(fn,STOP,count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+info['cleanup'],hex(fn)
    assert cpu.reg_read(UC_X86_REG_FPCW)==0x7f and last_error==0x12345678
    assert bytes(cpu.mem_read(0,4))==struct.pack('<I',0xa5a5a5a5)
    after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
    for at,length in writes:
        data=after[at-BASE:at-BASE+length];expected[at-BASE:at-BASE+length]=data;outputs.append([at,data.hex()])
    assert after==expected,('unexpected write',hex(fn))
    result=bytes(cpu.mem_read(OUTPUT,8)).hex() if info['result']=='double' else cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff) if info['result']!='void' else None
    cases.append({'fn':hex(fn),'this':this,'args':list(args),'patches':list(patches),'outputs':outputs,'result':result,
        'flag':cpu.mem_read(0x7ce4fd,1)[0],'errno':struct.unpack('<i',cpu.mem_read(TLS+8,4))[0],'events':dict(events),'original_acos_inputs':list(acos_inputs),
        'matrix_infinity_calls':list(matrix_infinity_calls)})
    counts[info['name']]+=1

values=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x3f7fffff,0xbf7fffff,0x3f800001,0xbf800001,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
values += [bits(i/1024) for i in range(-1024,1025)]
values += [rng.randrange(2**32) for _ in range(1024)]
for value in values:run(0x403ef0,args=[value])
identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
for i in range(3072):
 yaw=rng.uniform(-math.pi,math.pi);s,c=math.sin(yaw),math.cos(yaw)
 matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,1,2,3,1]
 if i<24:matrix=identity
 # The normal need not be unit for the original clamp; W never enters its dot.
 n=[rng.uniform(-2,2) for _ in range(3)]+[rng.choice([0,1,7])]
 if i<24:n=[frombits([0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x3f7fffff,0xbf7fffff,0x3f800001,0xbf800001,0x7f800000,0xff800000,0x7fc12345,0x7f812345][i%14]),0,0,7]
 if i%31==0:n[1]=float('nan')
 if i%31==1:n[2]=1e30
 velocity=[rng.uniform(-100,100),rng.choice([0,1,-1]),rng.uniform(-100,100),rng.choice([0,1,7])]
 if i%41==0:velocity=[1e30,0,-1e30,7]
 fraction=rng.choice([0.,-0.,.2,1.,-1.,1e-30,float('nan')])
 rate_value=rng.choice([0.,-0.,.1,1.,-1.,2.5,1e-30,1e30,float('nan'),2**24+1,2**31-1,-2**31+1])
 kind=1 if isinstance(rate_value,int) else 2;rate_bits=rate_value&0xffffffff if kind==1 else bits(rate_value)
 output=[turn,vectors+4,body+0xac,body+0xb4,body+0x6c,physics+0x2c][i%6]
 normal=[vectors,body+0x8c,body+0x7c,physics+0x18][i%4]
 p=[patch(body+0x6c,'<16f',*matrix),patch(body+0xac,'<4f',*velocity),
    patch(physics+0x18,'<16f',*(identity if i%2 else matrix)),patch(vectors,'<4f',*n),
    patch(rate+1,'<B',kind),patch(rate+12,'<I',rate_bits)]
 run(0x5039f0,args=[normal,output,bits(fraction)],patches=p,writes=[(body+0x6c,80),(physics+0x18,64),(output,4)])
assert coverage['0x623630']==3072 and coverage['0x5df4ac']==6144 and coverage['0x62bc7d']
scope='Original wall-tangent turn, including velocity and both matrices, folded return angle and aliased output; heading polynomial approximation. Real numeric/CRT callees. Infinity at matrix trig entry follows Intel masked-invalid NaN behavior, with raw emulator outputs retained and differences recorded. Constructed states; no full movement loop or physical x87 accuracy claim.'
fixture={'base':BASE,'memory':'wall-turn-memory.bin','globals':prior['globals'],'functions':functions,'cases':cases,
 'float_ranges':[[body+0x6c,80],[physics+0x18,64],[vectors,128],[turn,4]],'coverage':dict(coverage),'scope':scope,
 'matrix_infinity_specification':'Intel SDM Vol. 1, table 8-10: masked invalid FSIN/FCOS(infinity) yields QNaN. In premultiplied Y rotations, matrix rows 0 and 2 therefore contain NaNs. All other fields compare with the unmodified oracle.',
 'matrix_infinity_source':'https://cdrdv2-public.intel.com/868137/325462-089-sdm-vol-1-2abcd-3abcd-4.pdf'}
path=out/'wall-turn-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',dict(counts),'OS services',dict(os_calls),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_wall_turn_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'os_services':dict(os_calls),
 'x87_control_word':'0x007f','mxcsr':'0x1f80','scope':scope,
 'matrix_infinity_cases':sum(bool(c['matrix_infinity_calls']) for c in cases),
 'matrix_infinity_specification':fixture['matrix_infinity_specification'],'matrix_infinity_source':fixture['matrix_infinity_source'],
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'wall-turn-memory.bin']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
