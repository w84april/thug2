"""Recover the downward ground update with real collision, stat and timer callees.

D3DX's original SSE multiply backend is selected explicitly in the dispatch slot.
CPU/registry detection and the frame-counter producer are outside these checks.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'ground.json';report_path.unlink(missing_ok=True)
old=json.loads((out/'skater-fixtures.json').read_text());a=old['addresses'].copy();base=old['loader']
a.update(matrix=0x2002000,axis=0x2002100,left=0x2002200,right=0x2002300,skater_state=0x1630000,gate=0x1640000)
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS=[a[k] for k in ('data','grid','scene','scenes','runtime','nodes','owners','refs')]
BODY,PHYSICS,HEAP,MATRIX,AXIS,LEFT,RIGHT,STATE,GATE=[a[k] for k in ('body','physics','heap','matrix','axis','left','right','skater_state','gate')]
STACK,STOP,QUERY_STATE,STAMP=0x3000000,0x3f00000,0x691968,0x693998
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(DATA,0xa00000),(0x2000000,0x600000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
rng=random.Random(0x504b40);events=Counter();totals=Counter()
fixture={'addresses':a,'loader':base,'helpers':[],'timers':[],'release':[],'world':[],
    'owners':old['owners'],'references':old['references']}
def raw(at,n):return bytes(cpu.mem_read(at,n))
def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
def word(at):return struct.unpack('<I',raw(at,4))[0]
def floats(values):return struct.pack('<'+'f'*len(values),*values)
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def call(fn,this,args=(),cleanup=0):
    sp=STACK+0x18000;put(sp,'<'+'I'*(len(args)+1),STOP,*args)
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
    cpu.reg_write(UC_X86_REG_FPCW,0x7f);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
    cpu.emu_start(fn,STOP,count=5000000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+cleanup,hex(fn)
    assert raw(0,4)==bytes(4),'Exception chain not restored'
    return cpu.reg_read(UC_X86_REG_EAX)
put(0x684fe4,'<I',0x5df4ac)
identity=[1,0,0,0,0,1,0,0,0,0,1,0,7,8,9,1]

# Original forward word-copy semantics include overlapping matrices and NaN bits.
for offset in [-16,-4,0,4,16,64]:
    for i in range(16):
        memory=bytes(rng.randrange(256) for _ in range(192));cpu.mem_write(MATRIX,memory)
        returned=call(0x404090,MATRIX+64+offset,[MATRIX+64],4);assert returned==MATRIX+64+offset
        fixture['helpers'].append({'kind':'copy','offset':offset,'input':memory.hex(),'output':raw(MATRIX,192).hex()})

for i in range(512):
    left=[rng.uniform(-10,10) for _ in range(16)];right=[rng.uniform(-10,10) for _ in range(16)]
    if i%32==0:left[i%16]=float('nan')
    if i%32==1:right[i%16]=float('inf')
    for alias in [0,1,2,3]:
        cpu.mem_write(LEFT,floats(left)+b'\xad'*32);cpu.mem_write(RIGHT,floats(right)+b'\xad'*32);cpu.mem_write(MATRIX,b'\xad'*80)
        target=[MATRIX,LEFT,RIGHT,LEFT+4][alias]
        assert call(0x5df4ac,0,[target,LEFT,RIGHT],12)==target
        fixture['helpers'].append({'kind':'multiply','alias':alias,'left':floats(left).hex(),'right':floats(right).hex(),
            'out':raw(MATRIX,80).hex(),'left_after':raw(LEFT,96).hex(),'right_after':raw(RIGHT,96).hex()})

axes=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,7],[1,2,3,1],[1e-30,1e-30,0,1],
    [1e30,2e30,-3e30,0],[float('nan'),1,0,1],[float('inf'),1,2,1]]
angles=[0.,-0.,1e-20,1e-7,.001,.1,math.pi/2,math.pi,-math.pi,2*math.pi,100,1e6,float('nan')]
rotation_cases=[(axis,angle) for axis in axes for angle in angles]
rotation_cases += [([rng.uniform(-10,10) for _ in range(4)],rng.uniform(-20,20)) for _ in range(768)]
for axis,angle in rotation_cases:
    cpu.mem_write(AXIS,floats(axis));cpu.mem_write(MATRIX,b'\xad'*80)
    assert call(0x404c60,0,[MATRIX,AXIS,bits(angle)])==MATRIX
    assert raw(MATRIX+64,16)==b'\xad'*16 and raw(AXIS,16)==floats(axis)
    fixture['helpers'].append({'kind':'axis','axis':floats(axis).hex(),'angle':bits(angle),'output':raw(MATRIX,64).hex()})
    matrix=identity if len(fixture['helpers'])%2 else [rng.uniform(-2,2) for _ in range(16)]
    cpu.mem_write(MATRIX,floats(matrix)+b'\xad'*16)
    assert call(0x405950,MATRIX,[AXIS,bits(angle)],8)==MATRIX
    assert raw(MATRIX+64,16)==b'\xad'*16 and raw(AXIS,16)==floats(axis)
    fixture['helpers'].append({'kind':'rotate','axis':floats(axis).hex(),'angle':bits(angle),'input':floats(matrix).hex(),'output':raw(MATRIX,64).hex()})

def timer(config):
    counter,fps,origin,scale,offset=config
    put(0x7d1ec8,'<2I',counter,0xabadcafe);put(0x684fd0,'<I',fps);put(0x696d64,'<I',origin);put(0x67d7c0,'<I',scale);put(0x696d60,'<I',offset)
for i in range(3072):
    counter=([0,1,59,60,2**24+1,2**31-1,2**31,2**32-1]+[rng.randrange(2**32)])[i%9]
    config=[counter,bits(rng.choice([.5,24,30,50,60,59.94,144,1000])),rng.choice([0,1,0xffffffff,rng.randrange(2**32)]),
        bits(rng.choice([0.,1.,.125,1.5,-1.,2**-100,1e12,float('nan'),float('inf')])),rng.randrange(2**32)]
    timer(config);frame=call(0x5be970,0);elapsed=call(0x44ece0,0)
    fixture['timers'].append({'config':config,'frame':frame,'elapsed':elapsed})

# Probe destructor: detached, head, middle and tail references, plus repeated use.
PROBE=a['probe'];REF=PROBE+0x98
for variant in range(5):
    cpu.mem_write(PROBE,b'\xad'*192);cpu.mem_write(OWNERS,b'\xad'*32);cpu.mem_write(REFS,b'\xad'*48)
    if variant==0:put(REF,'<I',0)
    else:
        chain={1:[REF,REFS,REFS+16],2:[REFS,REF,REFS+16],3:[REFS,REFS+16,REF],4:[REF]}[variant]
        put(OWNERS+4,'<I',chain[0])
        for i,at in enumerate(chain):put(at,'<3I',OWNERS,chain[i-1] if i else 0,chain[i+1] if i+1<len(chain) else 0)
    record={'probe':raw(PROBE,192).hex(),'owners':raw(OWNERS,32).hex(),'refs':raw(REFS,48).hex()}
    call(0x41c350,PROBE);record.update(probe_after=raw(PROBE,192).hex(),owners_after=raw(OWNERS,32).hex(),refs_after=raw(REFS,48).hex())
    call(0x41c350,PROBE)
    assert raw(PROBE,192).hex()==record['probe_after'] and raw(OWNERS,32).hex()==record['owners_after'] and raw(REFS,48).hex()==record['refs_after']
    fixture['release'].append(record)

# Reuse the independently verified stat graph, rebinding its object entries to
# this test's skater. Add a real named parameter symbol; all callees execute.
stats_fixture=json.loads((out/'stats-fixtures.json').read_text());SB=stats_fixture['base'];stat_memory=bytearray((out/stats_fixture['memory']).read_bytes())
def sw(at):return struct.unpack_from('<I',stat_memory,at-SB)[0]
def sp(at,value):struct.pack_into('<I',stat_memory,at-SB,value)
stat_object=next(c['this'] for c in stats_fixture['cases'] if c['fn']=='0x580490')
parameters=next(c['args'][0] for c in stats_fixture['cases'] if c['fn']=='0x5805b0')
globals_={name:(address,value) for name,address,value in stats_fixture['globals']}
manager=globals_['thug_object_lookup_manager'][1]
for table in [sw(manager+8),sw(manager+12)]:
    buckets=sw(table+4)
    for i in range(16):
        node=buckets+i*12
        while node:
            if sw(node)==23 and sw(node+4):sp(node+4,BODY)
            node=sw(node+8)
EXTRA=SB+len(stat_memory);symbol_name=0xe7116a96;bucket=SB+(symbol_name&4095)*4
old_head=sw(bucket);sp(bucket,EXTRA);stat_memory.extend(struct.pack('<BBHIIII',0,10,0,symbol_name,0,parameters,old_head))
# Modify the default parameter set to contain the new named structure.
default=sw(SB+(0x8cbc89dd&4095)*4)
while sw(default+4)!=0x8cbc89dd:default=sw(default+16)
root=sw(default+12);member=sw(root+4);sp(member+4,symbol_name)
# A practical upright rate comes from the original stat formula, not a stub.
basepair=sw(sw(parameters+4)+8);struct.pack_into('<2f',stat_memory,basepair+4-SB,.5,1.5)
cpu.mem_write(SB,bytes(stat_memory));fixture['stat_base']=SB;fixture['stat_globals']=stats_fixture['globals']
(out/'ground-stats.bin').write_bytes(stat_memory)
for _,at,value in stats_fixture['globals']:put(at,'<I',value)
cpu.mem_write(DATA,(out/base['loaded']).read_bytes());cpu.mem_write(GRID,(out/base['grid']).read_bytes());heap=(out/base['heap']).read_bytes()
cpu.mem_write(SCENE,b'\0'*0xd4+struct.pack('<I',GRID));put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(0x6fa7ec,'<I',SCENES);put(0x691984,'<I',NODES);put(0x691974,'<I',0)
cpu.mem_write(0x67c6b8,struct.pack('<2048H',*range(2048)))
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
def observe(uc,address,size,user):
    names={0x4172f0:'probes',0x44ece0:'timer_reads',0x580790:'stat_reads',0x405950:'rotations',0x4637e0:'reference_unlinks'}
    if address in names:events[names[address]]+=1
    elif address==0x504c00:events['hits']+=bool(uc.reg_read(UC_X86_REG_EAX)&255)
    elif address==0x504cc3:events['accepted_hits']+=1
    elif address==0x504c48:events['flag8_rejections']+=1
    elif address==0x504c99:events['normal_rejections']+=1
for address in [0x4172f0,0x44ece0,0x580790,0x405950,0x4637e0,0x504c00,0x504cc3,0x504c48,0x504c99]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
cpu.ctl_flush_tb()

def world(test,index,variant):
    events.clear();cpu.mem_write(HEAP,heap);cpu.mem_write(OWNERS,bytes.fromhex(old['owners']));cpu.mem_write(REFS,bytes.fromhex(old['references']))
    cpu.mem_write(RUNTIME,bytes.fromhex(test['actors']));body=bytearray(bytes.fromhex(test['body'])+b'\xad'*(0x2c0-0xbc))
    physics=bytearray(bytes.fromhex(test['physics'])+b'\xad'*(0x1540-0x318));state=bytearray(b'\xad'*0x98)
    struct.pack_into('<I',body,0x14,23);body[0xbc]=0;body[0x110]=0;struct.pack_into('<I',body,0x100,PHYSICS)
    body[0x278:0x2b0]=stat_memory[stat_object+0x278-SB:stat_object+0x2b0-SB];struct.pack_into('<I',body,0x280,PHYSICS)
    struct.pack_into('<I',physics,4,0x5bd63b29);struct.pack_into('<I',physics,16,0);struct.pack_into('<2I',physics,0x1528,STATE,GATE)
    struct.pack_into('<f',physics,0x8c,[1/30,1/60,1/144,0,-1/60][index%5]);physics[0x2ed]=0;physics[0x302]=0
    state[0x28]=0;state[0x30]=[0,1,128][index%3];state[0x78]=0;state[0x80]=[0,1,128][(index//3)%3]
    struct.pack_into('<f',body,0xb0,-10)
    # Raise the existing mesh position to exercise a downward hit; preserve X/Z.
    pos=list(struct.unpack_from('<4f',body,0x4c));pos[1]+=[0,100,250,499,600][index%5];struct.pack_into('<4f',body,0x4c,*pos)
    up=math.sqrt(.75);tilted=[1,0,0,0,0,.5,up,0,0,-up,.5,0,0,0,0,1]
    struct.pack_into('<16f',body,0x6c,*(tilted if variant%2 else identity))
    gate=bytearray(b'\xad'*0x28);struct.pack_into('<I',gate,0x18,0)
    if variant==2:state[0x78]=128
    if variant==3:struct.pack_into('<f',body,0xb0,10);struct.pack_into('<I',gate,0x18,1)
    if variant==4:struct.pack_into('<f',body,0xb0,float('nan'));struct.pack_into('<I',gate,0x18,1)
    if variant==5:struct.pack_into('<f',body,0x80,0.9)
    cpu.mem_write(BODY,bytes(body));cpu.mem_write(PHYSICS,bytes(physics));cpu.mem_write(STATE,bytes(state));cpu.mem_write(GATE,bytes(gate))
    config=[rng.randrange(2**32),bits(60),rng.randrange(2**32),bits(rng.choice([.5,1,1.5])),rng.randrange(2**32)];timer(config)
    cpu.mem_write(QUERY_STATE,bytes.fromhex(test['initial_state']));cpu.mem_write(STAMP,bytes([test['stamp']]));cpu.mem_write(0x691910,b'\0')
    cpu.mem_write(0x7ce4fd,b'\xad')
    call(0x504b40,PHYSICS)
    assert raw(OWNERS,96).hex()==old['owners'] and raw(REFS,48).hex()==old['references'],'Temporary moving reference leaked'
    assert raw(GATE,len(gate))==gate and raw(SB,len(stat_memory))==stat_memory
    assert events['stat_reads']==events['rotations']
    assert events['timer_reads']==(int(state[0x30]!=0)+int(state[0x80]!=1))*events['accepted_hits']
    if variant in [2,3]:assert not events['probes']
    fixture['world'].append({'object':test['object'],'variant':variant,'actors':test['actors'],'actors_after':raw(RUNTIME,0x300).hex(),
        'body':body.hex(),'body_after':raw(BODY,len(body)).hex(),'physics':physics.hex(),'physics_after':raw(PHYSICS,len(physics)).hex(),
        'skater_state':state.hex(),'skater_state_after':raw(STATE,len(state)).hex(),'gate':gate.hex(),'timer':config,
        'initial_state':test['initial_state'],'state':raw(QUERY_STATE,12).hex(),'stamp':test['stamp'],'final_stamp':raw(STAMP,1)[0],
        'stamps':bytes(raw(base['instances']+i*24+10,1)[0] for i in range(base['count'])).hex(),'events':dict(events),'gameplay_flag':raw(0x7ce4fd,1)[0]})
    totals['updates']+=1;totals.update(events)
for index,test in enumerate(old['world'][::3]):
    for variant in range(6):world(test,index,variant)
    if index%100==0:print(index,'training objects',dict(totals),flush=True)
assert totals['rotations'] and totals['accepted_hits'] and totals['reference_unlinks'],'Missing full-chain coverage'
path=out/'ground-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_ground_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(totals),'helper_cases':len(fixture['helpers']),'timer_cases':len(fixture['timers']),
    'probe_release_cases':len(fixture['release']),'x87_control_word':'0x007f','mxcsr':'0x1f80','runtime_control_words_observed_in_game':False,
    'scope':'Complete downward update using training collision, stat lookup, timers and original SSE matrix backend; constructed states, no full movement loop.',
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'ground-stats.bin']},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(totals))
