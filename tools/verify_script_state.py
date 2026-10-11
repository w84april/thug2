"""Script construction/list and wait scheduling against original x86 instructions.

Virtual component wait methods use explicit test instrumentation on both sides.
Every concrete game/timer callee executes normally. No token execution is claimed.
"""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'script-state.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP,OUTPUT=0x1800000,0x10000,0x3000000,0x3f00000,0x1805800
SCRIPTS=[BASE+0x100,BASE+0x300,BASE+0x500]
OWNER,OTHER,METHODS,LOG=BASE+0x800,BASE+0xa00,BASE+0x1000,BASE+0x4000
CALLBACK=STOP+0x100
rng=random.Random(0x473050);memory=bytearray(b'\xad'*0x6000)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def number(word):return struct.unpack('<f',struct.pack('<I',word))[0]
put(OWNER,'<4I',METHODS,0,0x55555555,OTHER);put(OTHER,'<4I',METHODS,1,0xaaaaaaaa,OWNER)
put(METHODS+24,'<I',CALLBACK);put(LOG,'<I',0)
for i,s in enumerate(SCRIPTS):
    put(s,'<2I',SCRIPTS[i+1] if i<2 else 0,SCRIPTS[i-1] if i else 0)
    put(s+0xc,'<I',0)
    put(s+0x98,'<I',0);put(s+0x9c,'<B',0);put(s+0xa0,'<f',0)
    put(s+0xa4,'<3I',0,0x12345678,OWNER)
initial=bytes(memory);(out/'script-state-memory.bin').write_bytes(initial)
globals_=[['thug_current_script',0x6f3530,4],['thug_script_list',0x6f3538,4],
    ['thug_script_count',0x6f353c,4],['thug_script_next_serial',0x6f3540,4],['thug_script_wait_gate',0x6f352c,1],
    ['thug_frame_length_scale',0x684fc8,4],['thug_frame_counter',0x7d1ec8,4],['thug_frame_rate',0x684fd0,4],
    ['thug_timer_origin',0x696d64,4],['thug_time_scale',0x67d7c0,4],['thug_timer_offset',0x696d60,4]]
defaults=[0,SCRIPTS[1],2,43,0,bits(1),120,bits(60),0,bits(1),0]
functions={}
def bind(at,name,this=True,result='void',cleanup=0):
    functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':cleanup}
bind(0x4738e0,'thug_script_initialize',result='word')
bind(0x4728c0,'thug_script_current',False,'word')
bind(0x4728d0,'thug_script_next',False,'word')
bind(0x4728f0,'thug_script_clear_wait')
bind(0x472940,'thug_script_has_instruction',result='byte')
bind(0x4739a0,'thug_script_set_object_wait',cleanup=12)
bind(0x473050,'thug_script_update_wait')
bind(0x5beaa0,'thug_frame_duration',False,'double')
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cpu.mem_write(CALLBACK,b'\xc2\x08\x00')
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
cases=[];counts=Counter();coverage=Counter();callbacks=0
def word(at):return struct.unpack('<I',cpu.mem_read(at,4))[0]
def setword(at,value):cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
def wait_callback(uc,address,size,user):
    global callbacks
    callbacks+=1;sp=uc.reg_read(UC_X86_REG_ESP);owner=uc.reg_read(UC_X86_REG_ECX);script=word(sp+4);arg=word(sp+8)
    index=word(LOG);assert index<16;setword(LOG,index+1)
    uc.mem_write(LOG+16+index*24,struct.pack('<6I',owner,script,arg,word(script+0xa4),word(script+0xac),word(owner+8)))
    mode=word(owner+4)
    if mode==1:setword(owner+8,word(owner+8)^0x80000000);setword(script+0xa4,0)
    elif mode==2:setword(script+0xa8,word(script+0xa8)^0x13579bdf);setword(script+0xa4,3)
    elif mode==3:setword(script+0xac,word(owner+12));setword(owner+8,word(owner+8)+arg);setword(script+0x98,arg)
cpu.hook_add(UC_HOOK_CODE,wait_callback,begin=CALLBACK,end=CALLBACK)
def observe(uc,address,size,user):coverage[hex(address)]+=1
for at in [0x4637b0,0x5beaa0,0x44ece0,0x5be970]:cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)

def case(calls,patches=(),global_changes=None):
    global callbacks
    expected=bytearray(initial);values=list(defaults)
    for key,value in (global_changes or {}).items():values[key]=value
    for at,data in patches:
        raw=bytes.fromhex(data);expected[at-BASE:at-BASE+len(raw)]=raw
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0,b'\xa5'*4)
    for (_,at,width),value in zip(globals_,values):cpu.mem_write(at,value.to_bytes(width,'little'))
    stages=[]
    for fn,this,args in calls:
        info=functions[hex(fn)];sp=STACK+0x18000
        cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP+32 if info['result']=='double' else STOP,*args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
        callbacks=0;cpu.emu_start(fn,STOP,count=200000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+info['cleanup'],hex(fn)
        assert bytes(cpu.mem_read(0,4))==b'\xa5'*4 and cpu.reg_read(UC_X86_REG_FPCW)==0x7f
        result=bytes(cpu.mem_read(OUTPUT,8)).hex() if info['result']=='double' else None if info['result']=='void' else cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff)
        if info['result']=='double':
            # The FSTP capture belongs to test machinery, not the function.
            cpu.mem_write(OUTPUT,bytes(expected[OUTPUT-BASE:OUTPUT-BASE+8]))
        after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
        # Record changed words, then compare every byte in the browser. Do not
        # exclude unchanged fields, guards, list nodes, method table or log tail.
        for offset in range(0,len(initial),4):
            if after[offset:offset+4]!=expected[offset:offset+4]:outputs.append([BASE+offset,after[offset:offset+4].hex()])
        expected=bytearray(after)
        final_globals=[int.from_bytes(cpu.mem_read(at,width),'little') for _,at,width in globals_]
        stages.append({'fn':hex(fn),'this':this,'args':args,'result':result,'outputs':outputs,'globals':final_globals,'callbacks':callbacks})
        counts[info['name']]+=1
    cases.append({'patches':list(patches),'globals':values,'steps':stages})
    return stages

s=SCRIPTS[0]
# New instance inserts at the head and consumes serial/count with unsigned wrap.
for i in range(96):
    changes={0:rng.choice([0,*SCRIPTS]),1:0 if i%2 else SCRIPTS[1],2:[0,1,0xfffffffe,0xffffffff][i%4],3:rng.randrange(2**32)}
    if i<4:changes[3]=[0,1,0xfffffffe,0xffffffff][i]
    p=[[s,bytes(rng.randrange(256) for _ in range(0xf4)).hex()]]
    case([(0x4738e0,s,[]),(0x4728c0,0,[]),(0x4728d0,0,[0]),(0x4728d0,0,[s]),(0x472940,s,[])],p,changes)
# Construct an empty list step by step, then traverse the actual resulting links.
case([(0x4738e0,p,[]) for p in SCRIPTS]+[(0x4728d0,0,[p]) for p in [0,*reversed(SCRIPTS)]],global_changes={1:0,2:0,3:0xffffffff})
for i in range(128):
    case([(0x472940,s,[]),(0x4728f0,s,[])],[patch(s+12,'<I',0 if i%3==0 else rng.randrange(2**32)),patch(s+0xa4,'<I',rng.randrange(2**32))])

# Setter preserves write order even where the owner's flags overlap the script.
for owner in [OWNER,s+0x90,s+0x98,s+0x9c,s+0xa0,s+0xa4]:
    for kind in [0,1,3,5,10,11,0xffffffff]:
        case([(0x4739a0,s,[kind,owner,rng.randrange(2**32)])])

# Frame waits and shared gate, including frames beyond signed int32 range.
for kind in [0,1,3,11,12,255,0xffffffff]:
    for frames in [0,1,2,3,0x7fffffff,0x80000000,0xffffffff]:
        for gate in [0,1,255]:
            case([(0x473050,s,[])]*4,[patch(s+0xa4,'<I',kind),patch(s+0x98,'<I',frames)],{4:gate})
case([(0x473050,p,[]) for p in SCRIPTS],
    [patch(p+0xa4,'<I',11) for p in SCRIPTS],{4:0})

numeric=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for value in numeric+[bits(i/8) for i in range(-128,129)]+[rng.randrange(2**32) for _ in range(256)]:
    case([(0x5beaa0,0,[])],global_changes={5:value})
# Timed tick waits: NaNs take the subtraction path; small positive waits must
# remain suspended for at least one update. Equality remains waiting at zero.
for i in range(1536):
    scale=numeric[i%len(numeric)] if i<144 else bits(rng.choice([0,1,-1,0.5,2,1e-30,1e30]))
    remaining=numeric[(i//12)%len(numeric)] if i<144 else bits(rng.choice([0,1,-1,0.01,0.01666666753590107,0.03333333507180214,1e-30,1e30]))
    p=[patch(s+0xa4,'<I',2),patch(s+0xa0,'<I',remaining),patch(s+0x9c,'<B',[0,1,255][i%3])]
    case([(0x473050,s,[])]*3,p,{5:scale})
# Absolute elapsed waits use the recovered timers, offset/wrap and exact FILD
# before comparing with a float. Include adjacent thresholds around uint32.
for i in range(1536):
    frame=rng.choice([0,1,59,60,61,2**24+1,2**31-1,2**31,0xffffffff])
    origin=rng.randrange(2**32);offset=rng.randrange(2**32);start=rng.randrange(2**32)
    limit=numeric[i%len(numeric)] if i<144 else bits(rng.choice([0,1,-1,2**24,2**24+2,2**31,2**32,1e30]))
    case([(0x473050,s,[])],[patch(s+0xa4,'<2I',4,start),patch(s+0xa0,'<I',limit)],
        {6:frame,7:bits(rng.choice([0.5,30,60,120,1000])),8:origin,9:bits(rng.choice([0,0.5,1,2])),10:offset})
# Component wait methods see the original this/script/argument and can change
# the owner for the next tick or stop waiting. Other wait types never dispatch.
for elapsed in [0,1,2**24-1,2**24,2**24+1,2**24+3,2**25+3,2**31-1,2**31,2**31+1,0xfffffffe,0xffffffff]:
    rounded=bits(float(elapsed))
    for limit in [max(0,rounded-1),rounded,rounded+1]:
        case([(0x473050,s,[])],[patch(s+0xa4,'<2I',4,0),patch(s+0xa0,'<I',limit)],
            {6:0,7:bits(60),8:0,9:bits(1),10:elapsed})
for scale in [0.5,1,2]:
    rounded=bits(scale*number(bits(1/60)))
    for limit in [rounded-1,rounded,rounded+1]:
        for waited in [0,1]:
            case([(0x473050,s,[])]*3,[patch(s+0xa4,'<I',2),patch(s+0xa0,'<I',limit),patch(s+0x9c,'<B',waited)],{5:bits(scale)})

# The callback is test instrumentation for the virtual dispatch contract.
for kind in range(5,11):
    for mode in range(4):
        for argument in [0,1,0x12345678,0xffffffff]:
            p=[patch(s+0xa4,'<3I',kind,argument,OWNER),patch(OWNER+4,'<I',mode)]
            case([(0x473050,s,[])]*3,p)

scope='Original script constructor/list access and complete wait-state update, including real timing callees and an instrumented virtual component method. Constructed script states; no QB token execution, script-file loader, or complete skating loop. PC24 timing assumptions and NaN classification apply.'
fixture={'base':BASE,'memory':'script-state-memory.bin','method_slot':METHODS+24,'globals':globals_,'functions':functions,
    'float_fields':[p+0xa0 for p in SCRIPTS],'cases':cases,'scope':scope}
path=out/'script-state-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';callback=out/'script-wait-fixture.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
    '-Wl,--no-entry,--import-memory,--export-all,--global-base=33554432',str(ROOT/'tools/script_wait_fixture.c'),'-o',str(callback)],check=True)
print('x86 complete:',dict(counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_state_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'scope':scope,'x87_control_word':'0x007f',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-state-memory.bin',callback]},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
