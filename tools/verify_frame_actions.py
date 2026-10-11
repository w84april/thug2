"""Original projectile, rotation-completion and special-expiration paths."""
from pathlib import Path
import itertools
from unicorn import Uc

# Build the established full skater/QB/network graph without running its corpus.
# Attach observation hooks once, to the final oracle produced by that setup.
original_add=Uc.hook_add;observers={};native_observers={}
def setup_hook(cpu,kind,callback,*args,**kw):
    begin=kw.get('begin',args[1] if len(args)>1 else 1)
    end=kw.get('end',args[2] if len(args)>2 else 0)
    if getattr(callback,'__name__','')=='observe':
        observers[begin,end]=(kind,args,kw);return 0
    if getattr(callback,'__name__','')=='native':
        native_observers[begin,end]=(kind,args,kw,callback);return 0
    return original_add(cpu,kind,callback,*args,**kw)
source=Path(__file__).with_name('verify_grounded_update.py').read_text().split('\nfor speed in [0,100]:')[0]
Uc.hook_add=setup_hook
try:exec(compile(source.replace("'grounded-update.json'","'frame-actions.json'"),'<frame action graph>','exec'))
finally:Uc.hook_add=original_add
for kind,args,kw in observers.values():oracle.cpu.hook_add(kind,oracle.observe,*args,**kw)
for (begin,end),(kind,args,kw,callback) in native_observers.items():
    if begin==end==NATIVE:frame_native=callback
    else:oracle.cpu.hook_add(kind,callback,*args,**kw)
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load

ROT,FLIP,FCOMP,FSTATES,MARK,MODE,TEXT=0x1661000,0x1661800,0x1661a00,0x1661b00,0x1662000,0x1662100,0x1662400
CLIENT2,PEER2,LINK2=0x1664000,0x1666500,0x1666a00
copy(ROT,bytes(0x2000));copy(CLIENT2,bytes(0x3000))
put(GCONTEXT+16,'<I',SKATER_STATE)
put(SKATER_STATE+4,'<I',0x43686585);put(SKATER_STATE+12,'<2I',BODIES,ROT)
put(ROT+4,'<I',0x286a8d26);put(ROT+12,'<2I',BODIES,FLIP)
put(FLIP+4,'<I',0x488af07a);put(FLIP+12,'<2I',BODIES,0);put(FLIP+0x1c,'<I',FCOMP)
put(FCOMP+0x34,'<I',FSTATES)
for i in range(3):
    at=FSTATES+i*0x100
    put(at+4,'<I',i+1 if i<2 else 0xffffffff)
    put(at+12,'<I',at+0x100 if i<2 else at)
    put(at+0x54,'<I',0xaabbccdd if i==0 else 0x11223344)
put(PHYS+0x1538,'<I',MARK);put(GATE+0x2c,'<I',MODE)
put(PHYS+0x2f4,'<B',1);put(PHYS+0x2f8,'<I',2)
put(PHYS+0x3a4,'<B',255);put(PHYS+0x2e4,'<B',255)
put(NAME_CONTEXT+0x998,'<2H',0,0)
copy(TEXT,b'projectile_control\0')
for axis in range(3):
    for entry in range(6):
        at=ROT+0x38+axis*0x94+entry*24
        copy(at,bytes((axis*37+entry*13+j)&255 for j in range(24)))
    put(ROT+0x38+axis*0x94+0x90,'<B',255)

NEW=[(0x478fb0,'thug_script_get_global_value_text',2,'word',False,False,False),
     (0x4fc3c0,'thug_skater_check_projectile_input',0,'byte',False,False,True),
     (0x4fc420,'thug_skater_is_walking',0,'word',False,False,True),
     (0x500820,'thug_skater_update_projectile',0,'void',True,True,True),
     (0x580480,'thug_skater_stat_modifier',0,'word',False,False,True),
     (0x500bc0,'thug_skater_update_special_timer',0,'void',True,True,True),
     (0x4208d0,'thug_rotation_clear',0,'void',True,True,True),
     (0x47dc40,'thug_animation_state_set_flipped',4,'byte',True,True,True),
     (0x419c10,'thug_animation_component_set_flipped',4,'byte',True,True,True),
     (0x5114f0,'thug_skater_toggle_flip',0,'void',True,True,True),
     (0x500900,'thug_skater_update_rotation',0,'void',True,True,True)]
for row in NEW:bind(*row)
for at in [r[0] for r in NEW]+[0x51fb90,0x51ebd0,0x51ecc0,0x4549f0,0x532ea0,0x459e50,0x4555f0,0x475790,0x477d40,0x409030,0x409070,0x477130]:
    if (at,at) not in observers:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
packet_data=[];special_parameters=0
def wire_observe(cpu,at,size,user):
    if at==0x4555f0:fields.add(cpu.reg_read(UC_X86_REG_ECX));return
    sp=cpu.reg_read(UC_X86_REG_ESP);spec=oracle.word(sp+4)
    kind=bytes(cpu.mem_read(spec,1))[0]
    if kind not in [0x2c,0x8c]:return
    length=int.from_bytes(cpu.mem_read(spec+2,2),'little')
    assert length=={0x2c:2,0x8c:1}[kind]
    packet_data.append([kind,bytes(cpu.mem_read(oracle.word(spec+4),length)).hex()])
for at in [0x459e50,0x4555f0]:oracle.cpu.hook_add(UC_HOOK_CODE,wire_observe,begin=at,end=at)
def check_parameters(cpu,at,size,user):
    global special_parameters
    sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
    if oracle.word(script+0xc8)==0x266b570c:
        # The terminal native command has no own arguments. Inspect the outer
        # script's real copied arguments, rather than its empty command params.
        member=oracle.word(oracle.word(script+0x14)+4)
        assert bytes(cpu.mem_read(member,1))[0]==26
        assert oracle.word(member+4)==0x70f16ea9 and oracle.word(member+8)==1
        special_parameters+=1
    frame_native(cpu,at,size,user)
oracle.cpu.hook_add(UC_HOOK_CODE,check_parameters,begin=NATIVE,end=NATIVE)
ranges={0x478fb0:28,0x4fc3c0:56,0x4fc420:28,0x500820:215,0x580480:10,
        0x500bc0:219,0x4208d0:375,0x47dc40:172,0x419c10:82,0x5114f0:116,0x500900:183}
instruction_hits=Counter()
def trace(cpu,at,size,user):instruction_hits[at]+=1
for at,length in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+length-1)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()

def config(key=0x20689278,tag=1):
    b=Build();b.symbol(crc('projectile_control'),tag,key)
    for name in [0x0ce5b783,0x3f356c63,0x266b570c]:
        code=b.alloc(b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
        entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
        previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
        link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,entry,link));b.symbol(name,7,code)
    return b
def history(rows=None,head=0,now=1666):
    rows=rows if rows is not None else [(0x20689278,2,0,0),(0x20689278,1,0,1)]
    p=[patch(NAME_CONTEXT+0x998,'<2H',len(rows),head)]
    for i,(key,kind,mask,age) in enumerate(rows):
        p.append(patch(NAME_CONTEXT+0x38+((head-i)%100)*24,'<4IB3sI',(now-age)&0xffffffff,kind,key,0xabcdef12,0,b'xyz',mask))
    return p
def network(player='local',slot=0,peer=1,active=True):
    p=online(active)+player_patches(0 if player=='missing' else 1)
    p += [patch(PLAYERS+0x1d0,'<I',{'local':1,'remote':0,'hidden':5,'missing':1}[player]),patch(BODIES+0x2bc,'<I',slot),patch(PEERS+0x60,'<I',peer)]
    if slot:
        p += [patch(NETWORK+8+slot*4,'<I',CLIENT2),patch(CLIENT2+8,'<I',12),queue_node(CLIENT2+0x1e8c,prev=LINK2,next_=LINK2),queue_node(LINK2,0x647578,PEER2,CLIENT2+0x1e8c,CLIENT2+0x1e8c),patch(PEER2+0x3c,'<I',9),patch(PEER2+0x60,'<I',peer)]
        for i in range(3):p.append(queue_node(PEER2+i*20,0x6474cc+i*4))
    return p
def run(at,this=PHYS,args=(),p=(),b=None,changes=None,label='frame action',repeat=1,floats=(),net=None):
    cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    stages=oracle.case(body_setup()+[call(at,this,args)]*repeat,
                      (b or config()).patches()+network(**(net or {}))+history()+list(p),
                      {index[k]:v for k,v in (changes or {}).items()})
    labels.append(label);previous=0
    for step in stages:
        step['float_fields']=list(floats);current=previous
        for address,data in step['outputs']:
            if address<=GOBS<address+len(data)//2:
                current=int.from_bytes(bytes.fromhex(data)[GOBS-address:GOBS-address+4],'little')
        step['callbacks']=current-previous;previous=current
    if len(labels)%50==0:print('Frame action cases',len(labels),flush=True)
    return stages[-1]

# The raw text getter intentionally returns payloads of all symbol types.
for tag in [0,1,2,3,4,5,6,7,8,9,10,11,12,14,255]:
    for value in [0,0x80000000,0x7f812345,0xffffffff]:
        r=run(0x478fb0,0,[TEXT,0x100],b=config(value,tag),label=f'raw symbol type {tag}')
        assert r['result']==value
run(0x478fb0,0,[TEXT,1],p=[patch(SYMBOLS+(crc('projectile_control')&0xfff)*4,'<I',0)],label='missing raw global')
for resolved in [False,True]:
    b=config(0x12345678,13)
    if resolved:b.symbol(0x12345678,2,0x7f812345)
    run(0x478fb0,0,[TEXT,1],b=b,label='resolved or missing alias')
for mode,alternate in itertools.product([0,1,2,0xffffffff],[0,1,255]):
    run(0x4fc420,GATE,p=[patch(MODE+0x1c,'<I',mode),patch(MODE+0x118,'<B',alternate)],label='walking mode and alternate byte')
for rows in [[],[(0x20689278,2,0,0)],[(77,2,0,0),(77,1,0,1)],[(0x20689278,2,0,1000)],None]:
    run(0x4fc3c0,p=history(rows),label='projectile input commits real history',repeat=2)
for key in [0,0x20689278,0xffffffff]:
    run(0x4fc3c0,p=history([(key,2,0,0),(key,1,0,1)]),b=config(key,13),label='projectile control unresolved alias retains raw checksum')
for field,value,width in [(PHYS+0x14c8,1,1),(PHYS+0x2f4,0,1),(SKATER_STATE+0x70,255,1),
                          (MARK+0x1c,1,1),(MARK+0x18,0xffffffff,4),(MARK+0x20,bits(1),4),
                          (MARK+0x20,0x7f812345,4)]:
    run(0x500820,p=[raw(field,value.to_bytes(width,'little')),patch(PHYS+0x14c4,'<I',3)],label='early projectile gates preserve cooldown')
for count,cooldown,mode in itertools.product([0,1,0x80000000,0xffffffff],[0,1,30,0xffffffff],[0,1]):
    run(0x500820,p=[patch(PHYS+0x2f8,'<I',count),patch(PHYS+0x14c4,'<I',cooldown),patch(MODE+0x1c,'<I',mode)],label='projectile signed inventory, countdown and walk/skate dispatch',repeat=2)
for target,value,width in [(PHYS+0x2f8,0,4),(PHYS+0x14c4,0,4),(PHYS+0x14c8,1,1),(PHYS+0x1518,NAME_CONTEXT+0x2000,4)]:
    run(0x500820,p=[patch(GOBS+4,'<4I',target,value,width,0),raw(NAME_CONTEXT+0x2000,bytes(0x1400))],label='projectile script changes live state',repeat=2)

for pointer in [0,GMODIFIER,GMODIFIER+0x100]:
    r=run(0x580480,BODIES,p=[patch(GMODOWNER+0x18,'<I',pointer)],label='modifier getter raw pointer')
    assert r['result']==pointer
for active,pointer in itertools.product([0,1,255],[0,GMODIFIER]):
    run(0x500bc0,p=[patch(PHYS+0x301,'<B',active),patch(GMODOWNER+0x18,'<I',pointer)],label='special active and null modifier gates')
for remaining,dt in itertools.product([0,-0.,-1,1e-40,.001,1,1e30,math.inf,-math.inf,math.nan],[0,1/60,1,-1,1e30]):
    run(0x500bc0,p=[patch(PHYS+0x301,'<B',1),patch(GMODIFIER,'<f',remaining),patch(PHYS+0x8c,'<f',dt)],label='special timer expiry and repeated frames',repeat=2,floats=[GMODIFIER])
for remaining,dt in [(1,math.nan),(math.inf,math.inf),(1,-math.inf),(3e38,-3e38),(1e-40,2e-40)]:
    run(0x500bc0,p=[patch(PHYS+0x301,'<B',1),patch(GMODIFIER,'<f',remaining),patch(PHYS+0x8c,'<f',dt)],label='special timer computed NaNs and exponent limits',repeat=2,floats=[GMODIFIER])
for target,value,width in [(PHYS+0x301,0,1),(GMODIFIER,bits(5),4),(GMODOWNER+0x18,0,4)]:
    run(0x500bc0,p=[patch(PHYS+0x301,'<B',1),patch(GMODIFIER,'<f',0),patch(GOBS+4,'<4I',target,value,width,0x266b570c)],label='special expiry script mutates live timer',repeat=2)

for player,slot,peer,active in itertools.product(['local','remote','hidden','missing'],[0,1],[0,1,8],[False,True]):
    run(0x4208d0,ROT,net={'player':player,'slot':slot,'peer':peer,'active':active},label='rotation clear through actual network queues',repeat=2)
for flipped,send,blocked in itertools.product([0,1,255,0x100,0x101,0xffffffff],[0,1,0x100,0x101],[0,1]):
    run(0x47dc40,FSTATES,[0x200,flipped,0xdeadbeef,send],p=[patch(FSTATES+0x28,'<I',blocked)],label='flip raw wire bytes and boolean stored bit',repeat=2)
for player in ['remote','missing','hidden']:
    run(0x47dc40,FSTATES,[0x200,255,0,1],net={'player':player},label='flip player visibility and local flag')
for count,flipped in itertools.product([0,1,2],[0,1,0x100,255]):
    p=[patch(FSTATES+count*0x100+4,'<I',0xffffffff)]
    run(0x419c10,FCOMP,[0x200,flipped,123,1],p=p,label='flip fanout and OR of old bits',repeat=2)
for flag,slot,offset in itertools.product([0,1,255],[0,1],[0,0xffffffff]):
    run(0x5114f0,FLIP,p=[patch(SKATER_STATE+0x28,'<B',flag)],net={'slot':slot},changes={0x696d60:offset},label='toggle flip with unconditional client lookup',repeat=2)
for active,mode,half in itertools.product([0,1,255],[0,1,2],[0,1]):
    run(0x500900,p=[patch(PHYS+0x2db,'<2B',active,half),patch(SKATER_STATE+0x18,'<I',mode),patch(PHYS+0x2e0,'<f',1),patch(PHYS+0x2e8,'<f',1)],label='rotation state transition, completion and half turn')
for remaining,step in itertools.product([0,-0.,-1,1e-40,19.999,20,20.001,21,1e30,math.inf,-math.inf,math.nan],[0,1,-1,1e30]):
    run(0x500900,p=[patch(PHYS+0x2db,'<2B',1,1),patch(PHYS+0x2e0,'<f',remaining),patch(PHYS+0x2e8,'<f',step),patch(SKATER_STATE+0x18,'<I',1)],label='rotation exact comparison thresholds and nonfinite values',repeat=2,floats=[PHYS+0x2e0])

pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,length in ranges.items():
    instructions=list(md.disasm(pe.get_data(at-0x400000,length),at))
    missing=[hex(i.address) for i in instructions if not instruction_hits[i.address]]
    coverage[hex(at)]={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing}
    # A null structure allocation falls through to a null member write in the
    # executable; successful allocation is the established internal contract.
    assert missing==(['0x500c48'] if at==0x500bc0 else []),(hex(at),missing)
assert special_parameters and packet_data
scope=('Complete projectile update500820, rotation completion500900 and special expiry500bc0, with raw global getter478fb0, '
       'projectile input4fc3c0, walking gate4fc420, modifier getter580480, rotation clear4208d0, animation flip47dc40/419c10 and '
       'skater toggle5114f0. Actual input history, synchronous QB, timer, allocation and network queue callees execute. '
       'Defined arena/global/heap/packet bytes compare exactly except declared computed NaNs. Terminal native QB, diagnostic '
       'and successful heap services remain explicit boundaries; valid components and sentinel lists are required. '
       'Not the complete movement dispatcher, renderer or playable level.')
fixture={'base':BASE,'memory':'frame-actions-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
         'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
         'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,
         'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,
         'pointer_fields':sorted(fields),'native_callbacks':[
             {'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},
             {'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'frame-actions-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
(out/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),
        'callee_coverage':dict(oracle.coverage),'instruction_coverage':coverage,'native_qb_calls':dict(qb_calls),
        'special_parameter_observations':special_parameters,'packets':packet_data,'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Original frame actions',len(labels),coverage,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_frame_actions_wasm.mjs'),str(out)],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS frame actions',len(labels),sum(oracle.counts.values()))
