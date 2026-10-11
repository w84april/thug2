"""Recover movement primitives against real x86 callees and constructed state.

No gameplay/parameter call is stubbed. This is not the full skater update.
"""
import hashlib,itertools,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'motion.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP,OUTPUT=0x1800000,0x20000,0x3000000,0x3f00000,0x2000600
rng=random.Random(0x4fe530);memory=bytearray(b'\xad'*SIZE);memory[:0x4000]=bytes(0x4000);cursor=0x4000
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+3)&~3;assert cursor<SIZE;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def word(at):return struct.unpack_from('<I',memory,at-BASE)[0]
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def symbol(name,kind,value):
    at=alloc(20);bucket=BASE+(name&4095)*4
    put(at,'<BBHIIII',0,kind,0,name,0,value,word(bucket));put(bucket,'<I',at);return at
def structure(entries):
    at=alloc(8);nodes=[alloc(16) for _ in entries];put(at,'<2I',0,nodes[0] if nodes else 0)
    for i,(name,kind,value) in enumerate(entries):put(nodes[i],'<4I',kind*2,name,value,nodes[i+1] if i+1<len(nodes) else 0)
    return at,nodes
def pair(x,y):
    at=alloc(16);put(at+4,'<2f',x,y);return at

body,physics,state,input_=alloc(0x2d0),alloc(0x1540),alloc(0x98),alloc(0x194)
modifier,owner=alloc(0x80),alloc(0x20)
network,game,settings,difficulty,flags=alloc(0x140),alloc(0x3e0),alloc(0x20),alloc(0x3a0),alloc(0x680)
manager,table,bucket=alloc(16),alloc(8),alloc(12)
vector=alloc(32)
put(body+0x14,'<I',23);put(body+0xbc,'<B',0);put(body+0x100,'<I',physics);put(body+0x110,'<B',0)
put(body+0x278,'<I',owner);put(body+0x280,'<I',physics);put(body+0x290,'<12f',*range(1,13))
put(owner+0x18,'<I',modifier);put(modifier+0x74,'<B',0)
put(physics+4,'<I',0x5bd63b29);put(physics+12,'<2I',body,0)
put(physics+0x150c,'<I',input_);put(physics+0x1528,'<I',state)
for offset in [0x2d9,0x2ed,0x302,0x303,0x310,0x311,0x388]:put(physics+offset,'<B',0)
put(physics+0x8c,'<f',1/60);put(physics+0x6c,'<f',1)
for offset in [0x20,0x28,0x30,0x78]:put(state+offset,'<B',0)
for offset in [0x40,0x60,0x80,0x180]:put(input_+offset,'<B',0)
put(network,'<I',0);put(game+0x20,'<I',flags);put(game+0x38c,'<I',difficulty);put(game+0x3d0,'<f',0)
put(flags+0x5f0,'<32I',*([0]*32))
MODE=0x77770001
s,settings_nodes=structure([(0x6dc3d6f1,1,1),(0xa1dc81f9,13,MODE),(0x5a2c589a,1,0)])
put(settings+4,'<2I',0,word(s+4))
s,difficulty_nodes=structure([(MODE,1,1)]);put(difficulty+0x398,'<I',s)
symbol(0x6357d57c,2,bits(9));symbol(0x6b0f24bc,1,0xaaa10001);symbol(0xaaa10001,1,33)
put(manager+8,'<2I',table,table);put(table,'<2I',0,bucket);put(bucket,'<3I',23,body,0)
stat_names=[0x4610c2e3,0x92e0247c,0x5f9b864d,0x3d24128e]
stat_pairs=[];stat_entries=[]
for i,name in enumerate(stat_names):
    p=pair([100,200,20,40][i],[300,500,120,240][i]);stat_pairs.append(p)
    s,_=structure([(0,5,p),(0,1,i)]);symbol(name,10,s);stat_entries.append((name,10,s))
numeric_names=[0x62a1fa03,0xc3527ef2,0xe5d73f6f,0xfaa40754,0xc31ca696,0x441c38a0,0x0ec128f0,0xbe33a41e]
numeric_values=[25,.25,100,-800,1,2,.5,1.5]
numeric={name:symbol(name,2,bits(value)) for name,value in zip(numeric_names,numeric_values)}
gravity_flag=symbol(0x9c8c6df1,1,65)
local_numeric=[(name,2,bits(value*1.25)) for name,value in zip(numeric_names[2:4]+[numeric_names[6]],numeric_values[2:4]+[numeric_values[6]])]
local_set,local_nodes=structure(stat_entries+local_numeric)
empty_set,_=structure([])
default_set=symbol(0x8cbc89dd,10,local_set)
alternate_set=symbol(0xd3d12913,10,empty_set)
identity=[1,0,0,0,0,1,0,0,0,0,1,0,7,8,9,1]
put(body+0x6c,'<16f',*identity);put(body+0xac,'<4f',0,0,100,1)
initial=bytes(memory[:cursor]);(out/'motion-memory.bin').write_bytes(initial)

pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(0x2000000,0x10000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
globals_=[('thug_script_symbol_buckets',0x6f3624,BASE),('thug_network_state',0x7cce14,network),
    ('thug_game_settings',0x7ce470,settings),('thug_game_context',0x7ce478,game),('thug_object_lookup_manager',0x6f0fc0,manager)]
for _,at,value in globals_:cpu.mem_write(at,struct.pack('<I',value))
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
functions={}
for address,name,result,cleanup in [(0x4fe320,'should_brake','byte',0),(0x4fe420,'braking_inhibited','byte',0),
        (0x4fe490,'can_accelerate','byte',0),(0x4fe530,'accelerate','void',0),(0x5019e0,'brake','void',0),
        (0x4ff590,'align_velocity','void',4),(0x4ff470,'gravity','double',0)]:
    functions[hex(address)]={'name':'thug_skater_'+name,'result':result,'cleanup':cleanup}
functions['0x5843a0']={'name':'thug_gameplay_flag_set','result':'void','cleanup':4}
functions['0x4023f0']={'name':'thug_vector_normalize','result':'word','cleanup':0}
functions['0x42bbf0']={'name':'thug_vector_set_length','result':'word','cleanup':4,'float_args':[0]}
cases=[];counts=Counter();trace=[];coverage=Counter()
def observe(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP);arg=struct.unpack('<I',bytes(uc.mem_read(sp+4,4)))[0]
    trace.append([hex(address),arg]);coverage[hex(address)]+=1
for address in [0x4fe420,0x580400,0x580790,0x5805b0,0x580490,0x478f00,0x478f60,0x584cc0,0x5843a0,0x4023f0,0x42bbf0]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
def run(fn,this=physics,args=(),patches=(),writes=()):
    info=functions[hex(fn)];expected=bytearray(initial)
    for at,data in patches:expected[at-BASE:at-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x7ce4fd,b'\xad');cpu.mem_write(0,struct.pack('<I',0xa5a5a5a5))
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP+32 if info['result']=='double' else STOP,*args))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    trace.clear();cpu.emu_start(fn,STOP,count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+info['cleanup'],hex(fn)
    assert bytes(cpu.mem_read(0,4))==struct.pack('<I',0xa5a5a5a5),'SEH chain must be restored'
    after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
    for at,length in writes:
        data=after[at-BASE:at-BASE+length];expected[at-BASE:at-BASE+length]=data;outputs.append([at,data.hex()])
    assert after==expected,('unexpected write',hex(fn))
    result=bytes(cpu.mem_read(OUTPUT,8)).hex() if info['result']=='double' else cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff) if info['result'] in ['byte','word'] else None
    cases.append({'fn':hex(fn),'this':this,'args':list(args),'patches':list(patches),'outputs':outputs,'result':result,
        'flag':cpu.mem_read(0x7ce4fd,1)[0],'trace':list(trace)})
    counts[info['name']]+=1

special=[0.,-0.,1e-20,1e-5,.49999997,.5,.50000006,24.999998,25.,25.000002,49.999996,50.,50.000004,
    100.,150.,1000.,-100.,float('nan'),float('inf'),-float('inf')]
vectors=[[0,0,v,1] for v in special]+[[rng.uniform(-500,500) for _ in range(4)] for i in range(128)]
# Exhaust every logical input combination; threshold values distinguish strict tests.
for v,combination in itertools.product(vectors[:20],itertools.product([0,128],repeat=6)):
    a,b,c,d,e,f=combination
    patches=[patch(body+0xac,'<4f',*v),patch(physics+0x2d9,'<B',a),patch(input_+0x180,'<B',b),
        patch(input_+0x40,'<B',c),patch(physics+0x311,'<B',d),patch(input_+0x60,'<B',e),patch(input_+0x80,'<B',f)]
    run(0x4fe320,patches=patches)
for i in range(256):
    p=[patch(body+0xac,'<4f',*[rng.uniform(-300,300) for _ in range(4)]),
        patch(body+0x8c,'<4f',*[rng.uniform(-2,2) for _ in range(4)]),patch(input_+0x40,'<B',1),
        patch(physics+0x311,'<B',1),patch(input_+0x60,'<B',i&1),patch(input_+0x80,'<B',(i>>1)&1)]
    run(0x4fe320,patches=p)
for i,v in enumerate(vectors):
    patches=[patch(body+0xac,'<4f',*v),patch(physics+0x6c,'<f',rng.choice([-.5,.25,1.,float('nan')])),
        patch(numeric[0x62a1fa03]+12,'<f',rng.choice([0,25,100,1000,float('nan')])),
        patch(numeric[0xc3527ef2]+12,'<f',rng.choice([-.5,.25,1,float('nan')]))]
    run(0x4fe420,patches=patches)
    for branch in range(8):
        p=patches+[patch(physics+0x2d9,'<B',branch&1),patch(input_+0x180,'<B',(branch>>1)&1),
            patch(input_+0x40,'<B',(branch>>2)&1),patch(physics+0x310,'<B',int(i%11==0)),
            patch(state+0x20,'<B',i%2),patch(physics+0x303,'<B',int(i%3==0))]
        if i%7==0:p+=[patch(stat_pairs[i%2]+4,'<2f',float('nan'),100)]
        run(0x4fe490,patches=p)
for alternate,threshold in [(0,120),(1,260)]:
    for delta in [-1,0,1]:
        p=[patch(body+0xac,'<4I',bits(threshold)+delta,0,0,0),patch(physics+0x2d9,'<B',1),
            patch(state+0x20,'<B',alternate)]
        run(0x4fe490,patches=p)

for i in range(768):
    v=vectors[i%len(vectors)]
    p=[patch(body+0xac,'<4f',*v),patch(body+0x8c,'<4f',*[rng.uniform(-2,2) for _ in range(4)]),
        patch(physics+0x388,'<B',i%2),patch(physics+0x8c,'<f',rng.choice([0,-1/60,1/60,1/144,1,float('nan')])),
        patch(state+0x20,'<B',(i//2)%2),patch(physics+0x303,'<B',int(i%7==0)),patch(modifier+0x74,'<B',int(i%5==0)),
        patch(body+0xbc,'<B',i%2),patch(physics+0x302,'<B',int(i%3==0)),
        patch(difficulty_nodes[0]+8,'<I',i%3)]
    if i%19==0:p+=[patch(stat_pairs[2+(i%2)]+4,'<2f',float('nan'),120)]
    run(0x4fe530,patches=p,writes=[(body+0xac,16)])
    # Exercise complete brake path with both local float and global exact-int parameters.
    p=[patch(body+0xac,'<4f',*v),patch(physics+0x8c,'<f',rng.choice([0,-1/60,1/60,1.,2.])),
        patch(physics+0x6c,'<f',rng.choice([-.5,.25,1.,float('nan')])),patch(body+0xbc,'<B',1),
        patch(physics+0x302,'<B',i%2),patch(numeric[0xe5d73f6f]+1,'<B',1 if i%3==0 else 2),
        patch(numeric[0xe5d73f6f]+12,'<I',rng.choice([0,100,2**24+1,2**31-1]) if i%3==0 else bits(rng.choice([0,10,100,-100,float('nan')])))]
    run(0x5019e0,patches=p,writes=[(body+0xac,16),(physics+0x324,1)])

# Boundary pairs enforce braking's strict stop threshold and inhibition tests.
for rate,dt in itertools.product([0,10,-10,100],[0,1/60,1,-1]):
    threshold=bits(abs(2*rate*dt))
    for speed_word in [max(0,threshold-1),threshold,threshold+1]:
        p=[patch(body+0xac,'<4I',0,0,speed_word,bits(7)),patch(physics+0x8c,'<f',dt),
            patch(local_nodes[4]+8,'<f',rate),patch(physics+0x6c,'<f',1)]
        run(0x5019e0,patches=p,writes=[(body+0xac,16),(physics+0x324,1)])
for value in [0.,.25,25.,100.,float('nan')]:
    for dv,dy in itertools.product([-1,0,1],repeat=2):
        at=bits(value)
        p=[patch(body+0xac,'<4I',max(0,at+dv),0,0,0),patch(physics+0x6c,'<I',max(0,at+dy)),
            patch(numeric[0x62a1fa03]+12,'<f',value),patch(numeric[0xc3527ef2]+12,'<f',value)]
        run(0x4fe420,patches=p)

# Aliasing with the forward axis, including partial overlap, must retain MOV order.
for i,v in enumerate(vectors):
    for target in [vector,body+0xac,body+0x88,body+0x8c,body+0x90,body+0x94]:
        p=[patch(body+0x8c,'<4f',*[rng.uniform(-2,2) for _ in range(4)]),patch(target,'<4f',*v)]
        run(0x4ff590,args=[target],patches=p,writes=[(target,16)])

for i in range(768):
    p=[patch(state+0x30,'<B',i&1),patch(state+0x78,'<B',(i>>1)&1),patch(body+0xb0,'<f',rng.choice([-100.,0.,100.,float('nan')])),
        patch(flags+0x5f8,'<I',2 if i&4 else 0),patch(body+0xbc,'<B',1),patch(physics+0x302,'<B',i%2),
        patch(numeric[0xbe33a41e]+12,'<f',rng.choice([0,1,-1,2,1e-30,float('nan'),float('inf')])),
        patch(numeric[0xc31ca696]+12,'<f',rng.choice([0,1,2,-1,float('nan')])),
        patch(numeric[0x441c38a0]+12,'<f',rng.choice([0,1,2,-1,float('nan')])),
        patch(numeric[0xfaa40754]+1,'<B',1 if i%3==0 else 2),patch(numeric[0xfaa40754]+12,'<I',0x80000001 if i%3==0 else bits(-800)),
        patch(numeric[0x0ec128f0]+1,'<B',1 if i%5==0 else 2),patch(numeric[0x0ec128f0]+12,'<I',2**24+1 if i%5==0 else bits(.5))]
    run(0x4ff470,patches=p)
for index in [-512,-33,-32,-1,0,1,31,32,33,65,127,255,511]:
    at=flags+0x5f0+(index>>5)*4
    for value in [0,0xffffffff,0x80000000,rng.randrange(2**32)]:
        run(0x5843a0,this=flags,args=[index&0xffffffff],patches=[patch(at,'<I',value)],writes=[(at,4)])

# The new braking chain exposed underflow in the old float-only length helper.
# Cover the entire finite float exponent range through actual original helpers.
extremes=[0.,-0.,2**-149,2**-126,1e-30,1e-20,1.,1e20,1e30,3e38,float('nan'),float('inf')]
for value,length in itertools.product(extremes,[0.,-0.,1.,-1.,1e-30,1e30,float('nan'),float('inf')]):
    values=[value,-value,value/2,7.]
    p=[patch(vector,'<4f',*values)]
    run(0x4023f0,this=vector,patches=p,writes=[(vector,16)])
    run(0x42bbf0,this=vector,args=[bits(length)],patches=p,writes=[(vector,16)])
    # Along-velocity acceleration calls the same normalization on large inputs.
    run(0x4fe530,patches=[patch(body+0xac,'<4f',*values),patch(physics+0x388,'<B',1)],writes=[(body+0xac,16)])

assert coverage['0x4023f0'] and coverage['0x42bbf0'] and coverage['0x5843a0'] and coverage['0x580490']
fixture={'base':BASE,'memory':'motion-memory.bin','globals':globals_,'functions':functions,'cases':cases,
    'float_ranges':[[body+0x6c,80],[vector,16]],'coverage':dict(coverage)}
path=out/'motion-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',dict(counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_motion_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'x87_control_word':'0x007f',
    'scope':'Eight new movement/flag routines plus two existing vector helpers with original parameter and stat callees; constructed input states, not a full movement loop.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'motion-memory.bin']},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
