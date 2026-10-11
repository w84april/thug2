"""Original component lookup, skating parameter selection and configured drag."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'skating-params.json';report_path.unlink(missing_ok=True)
BODY,PHYSICS,COMPONENTS,STATE,SYMBOLS,OUTPUT=0x1600000,0x1610000,0x1620000,0x1630000,0x1800000,0x2000600
STACK,STOP=0x3000000,0x3f00000
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BODY,0x40000),(SYMBOLS,0x20000),(0x2000000,0x10000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x580400);counts=Counter();observed=[]
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def word(at):return struct.unpack('<I',raw(at,4))[0]
def fbits(n):return struct.unpack('<I',struct.pack('<f',n))[0]
def floats(values):return struct.pack('<'+'f'*len(values),*values)
def call(fn,this,args=(),cleanup=0,numeric=False):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP+32 if numeric else STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
    cpu.emu_start(fn,STOP,count=2000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    return cpu.reg_read(UC_X86_REG_EAX)
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
put(0x6f3624,'<I',SYMBOLS)
fixture={'addresses':{'body':BODY,'physics':PHYSICS,'components':COMPONENTS,'state':STATE,'symbols':SYMBOLS},
    'global_structures':[],'component_cases':[],'scripts':[],'selections':[],'parameters':[],'drag':[]}

# Exercise the global structure getter on the earlier alias/collision graphs.
old=json.loads((out/'params-fixtures.json').read_text());old_memory=(out/'params-memory.bin').read_bytes()
assert old['addresses']['base']==SYMBOLS
cpu.mem_write(SYMBOLS,old_memory)
for name,_ in old['lookups']:
    for assert_missing in [0,1]:fixture['global_structures'].append([name,assert_missing,call(0x479020,0,[name,assert_missing])])
assert raw(SYMBOLS,len(old_memory))==old_memory

body=bytearray(b'\xad'*0x104);struct.pack_into('<I',body,0x100,COMPONENTS);body[0xbc]=1
physics=bytearray(b'\xad'*0x152c)
struct.pack_into('<I',physics,4,0x5bd63b29);struct.pack_into('<I',physics,12,BODY);struct.pack_into('<I',physics,16,0)
struct.pack_into('<I',physics,0x1528,STATE)
components=bytearray(b'\xad'*0xc0)
for i,kind in enumerate([0x111,0x222,0x111]):
    struct.pack_into('<5I',components,i*64,0,kind,0,BODY,COMPONENTS+(i+1)*64 if i<2 else PHYSICS)
cpu.mem_write(BODY,bytes(body));cpu.mem_write(PHYSICS,bytes(physics));cpu.mem_write(COMPONENTS,bytes(components));cpu.mem_write(STATE,b'\xad'*0x24)
fixture.update(body_initial=body.hex(),physics_initial=physics.hex(),component_memory=components.hex())
for head in [0,COMPONENTS,COMPONENTS+64,COMPONENTS+128,PHYSICS]:
    for name in [0x111,0x222,0x5bd63b29,0,0xffffffff]+[rng.randrange(2**32) for _ in range(16)]:
        put(BODY+0x100,'<I',head)
        fixture['component_cases'].append([head,name,call(0x45db90,BODY,[name],4)])
put(BODY+0x100,'<I',COMPONENTS)
assert raw(PHYSICS,len(physics))==physics and raw(COMPONENTS,len(components))==components

A,B,GLOBAL_INT,GLOBAL_ALIAS=0xbed96eda,0x1a78b6fc,0xd00dad00,0xd00dae00
set_names=[0x8cbc89dd,0x8b3b782b,0x05716042,0x8711bc92,0x871ffb73,0x43da544e,0x08c9ad5e,0xd3d12913]
modes=[0,0x3029fb1f,0x61c62b2d,0x86929898,0xb2c99bf0,0x906f06e2,0xd8d2d646,0x14a3a4cf,0x8c7873d0,0x6cd38bbb]
def make_script(profile):
    image=bytearray(0x20000);cursor=0x4000
    def allocate(n):
        nonlocal cursor
        at=SYMBOLS+cursor;cursor+=n;return at
    def write(at,fmt,*values):struct.pack_into(fmt,image,at-SYMBOLS,*values)
    def symbol(name,kind,value):
        at=allocate(20);bucket=(name&4095)*4;next_=struct.unpack_from('<I',image,bucket)[0]
        write(at,'<BBHIIII',0,kind,0,name,0,value,next_);struct.pack_into('<I',image,bucket,at)
    def structure(entries):
        at=allocate(8);nodes=[allocate(16) for _ in entries];write(at,'<2I',0,nodes[0] if nodes else 0)
        for i,(name,kind,value) in enumerate(entries):write(nodes[i],'<4I',kind*2+(i&1),name,value,nodes[i+1] if i+1<len(nodes) else 0)
        return at
    symbol(A,2,fbits(.00011));symbol(B,2,fbits(.00023));symbol(GLOBAL_INT,1,16777217);symbol(GLOBAL_ALIAS,13,GLOBAL_INT)
    symbol(0xabba0001,2,fbits(.00003));symbol(0xabba0002,1,-1&0xffffffff)
    for i,name in enumerate(set_names):
        entries=[]
        if profile==0:entries=[(A,2,fbits(.00005*(i+1))),(B,2,fbits(.00007*(i+1)))]
        elif profile==1:entries=[(A,1,i+1),(B,1,(-i-1)&0xffffffff)]
        elif profile==2:entries=[(A,13,0xabba0001),(B,13,0xabba0002)]
        elif profile==4:entries=[(A,4,0x12345678),(B,10,0x12345678)]
        elif profile==5:
            nested=structure([(A,1,16777217),(B,2,fbits(.00002*(i+1)))])
            symbol(0xaaaa0000+i,10,nested)
            entries=[(A,2,fbits(.001)),(0,13,0xaaaa0000+i),(A,2,fbits(.00001*(i+1)))]
        elif profile==6:entries=[(A,2,0x7fc12345),(B,2,0x7f800000)]
        elif profile==7:entries=[(A,1,16777217),(B,1,(-16777217)&0xffffffff)]
        root=structure(entries)
        if i==0:symbol(0xfeed1001,10,root);symbol(name,13,0xfeed1001)
        else:symbol(name,10,root)
    symbol(set_names[0]+0x1000,1,42)  # Same-bucket collision before the default set.
    return bytes(image[:cursor])
scripts=[make_script(i) for i in range(8)];fixture['scripts']=[x.hex() for x in scripts]
def configure(case):
    cpu.mem_write(BODY,bytes(body)+b'\xad'*16);cpu.mem_write(PHYSICS,bytes(physics)+b'\xad'*16)
    cpu.mem_write(BODY+0xbc,bytes([case['enabled']]))
    cpu.mem_write(PHYSICS+0x2ed,bytes([case['active']]));put(PHYSICS+0x2f0,'<I',case['mode'])
    cpu.mem_write(PHYSICS+0x302,bytes([case['fallback']]))
    return 0 if case.get('null_body') else BODY
mode_values=sorted(set(modes+[x+d for x in modes[1:] for d in (-1,1)]+[rng.randrange(2**32) for _ in range(32)]))
for profile in [0,5]:
    cpu.mem_write(SYMBOLS,scripts[profile])
    for mode in mode_values:
        for enabled in [0,1,128]:
            for active,fallback in [(0,0),(0,1),(0,255),(1,0),(1,1),(255,255)]:
                case=dict(profile=profile,mode=mode,enabled=enabled,active=active,fallback=fallback)
                ptr=configure(case);before_body=raw(BODY,0x114);before_physics=raw(PHYSICS,0x153c)
                case['selected']=call(0x5802e0,0,[ptr]);fixture['selections'].append(case)
                assert raw(BODY,0x114)==before_body and raw(PHYSICS,0x153c)==before_physics
    case=dict(profile=profile,mode=0,enabled=0,active=0,fallback=0,null_body=True)
    case['selected']=call(0x5802e0,0,[configure(case)]);fixture['selections'].append(case)
    assert raw(SYMBOLS,len(scripts[profile]))==scripts[profile]

for profile,script in enumerate(scripts):
    cpu.mem_write(SYMBOLS,script)
    for index,mode in enumerate(modes):
        for name in [A,B,GLOBAL_INT,GLOBAL_ALIAS,0,0xffffffff]:
            for assert_missing in [0,1]:
                case=dict(profile=profile,mode=mode,enabled=1,active=1,fallback=index%2,name=name,assert_missing=assert_missing)
                ptr=configure(case);before_body=raw(BODY,0x114);before_physics=raw(PHYSICS,0x153c)
                call(0x580400,0,[name,assert_missing,ptr],numeric=True);case['output']=raw(OUTPUT,8).hex()
                fixture['parameters'].append(case)
                assert raw(BODY,0x114)==before_body and raw(PHYSICS,0x153c)==before_physics
    assert raw(SYMBOLS,len(script))==script

def observe(uc,address,size,user):
    observed.append([address,word(uc.reg_read(UC_X86_REG_ESP)+4)])
for address in [0x580400,0x4fe1f0]:cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
cpu.ctl_flush_tb()  # Parameter calls above have already translated these blocks.
flags=[0.,-0.,1.,-1.,1e-30,float('nan'),float('inf')]
for i in range(3072):
    profile=i%8;cpu.mem_write(SYMBOLS,scripts[profile])
    case=dict(profile=profile,mode=modes[(i//8)%len(modes)],enabled=rng.choice([0,1,255]),active=rng.choice([0,1,128]),fallback=rng.choice([0,1,255]))
    configure(case)
    velocity=[rng.uniform(-1000,1000) for _ in range(3)]+[rng.choice([0,1,-1,7])]
    if i%32==0:velocity=[0,0,0,1]
    elif i%32==1:velocity=[1e-4,0,0,1]
    elif i%32==2:velocity=[float('nan'),1,2,1]
    elif i%32==3:velocity=[float('inf'),1,2,1]
    dt=rng.choice([0,1/30,1/60,1/144,-1/60]);flag=flags[(i//8)%len(flags)]
    override=rng.choice([0,.00001,.001,1,-.001]);selector=rng.choice([0,1,128,255])
    cpu.mem_write(BODY+0xac,floats(velocity));put(PHYSICS+0x8c,'<f',dt);put(PHYSICS+0x350,'<f',flag);put(PHYSICS+0x35c,'<f',override)
    cpu.mem_write(STATE,b'\xad'*0x24);cpu.mem_write(STATE+0x20,bytes([selector]))
    before_body=raw(BODY,0x114);before_physics=raw(PHYSICS,0x153c);before_state=raw(STATE,0x24)
    observed.clear();call(0x4fe6a0,PHYSICS)
    assert [x[0] for x in observed]==[0x580400,0x580400,0x4fe1f0] and [x[1] for x in observed[:2]]==[A,B]
    assert raw(BODY,0xac)==before_body[:0xac] and raw(BODY+0xbc,0x58)==before_body[0xbc:]
    assert raw(PHYSICS,0x153c)==before_physics and raw(STATE,0x24)==before_state
    assert raw(COMPONENTS,len(components))==components and raw(SYMBOLS,len(scripts[profile]))==scripts[profile]
    case.update(velocity=floats(velocity).hex(),time_step=dt,override_flag=fbits(flag),override=override,selector=selector,
        output=raw(BODY+0xac,16).hex(),coefficient=observed[-1][1])
    fixture['drag'].append(case);counts['drag_calls']+=1;counts['parameter_reads']+=2
    if i%512==0:print(i,'configured drag cases',flush=True)
path=out/'skating-params-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_skating_params_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'global_structures':len(fixture['global_structures']),
    'component_cases':len(fixture['component_cases']),'selections':len(fixture['selections']),'parameter_cases':len(fixture['parameters']),
    'scope':'Full script-selected drag chain with constructed component lists and QB symbol graphs; script file loading, stat evaluation and full movement loop remain unrecovered.',
    'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('source_hashes',)},indent=2))
