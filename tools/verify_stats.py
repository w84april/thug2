"""Differential checks for the complete stat path and its original dependencies.

Constructed data graphs, real unmodified x86 callees. No gameplay call is stubbed.
"""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'stats.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP,OUTPUT=0x1800000,0x30000,0x3000000,0x3f00000,0x2000600
rng=random.Random(0x580790);image=bytearray(b'\xad'*SIZE);image[:0x4000]=bytes(0x4000);cursor=0x4000
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+3)&~3;assert cursor<SIZE;return at
def put(at,fmt,*values):struct.pack_into(fmt,image,at-BASE,*values)
def word(at):return struct.unpack_from('<I',image,at-BASE)[0]
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def symbol(name,kind,value):
    at=alloc(20);bucket=BASE+(name&4095)*4
    put(at,'<BBHIIII',0,kind,0,name,0,value,word(bucket));put(bucket,'<I',at);return at
def structure(entries):
    at=alloc(8);nodes=[alloc(16) for _ in entries];put(at,'<2I',0,nodes[0] if nodes else 0)
    for i,(name,kind,value) in enumerate(entries):put(nodes[i],'<4I',kind*2+(i&1),name,value,nodes[i+1] if i+1<len(nodes) else 0)
    return at,nodes
def pair(x,y):
    at=alloc(32);put(at+4,'<2I',bits(x),bits(y));return at

body,physics,state,stats=alloc(0x124),alloc(0x1540),alloc(0x40),alloc(0x2c0)
modifier,owner=alloc(0x84),alloc(0x28)
network,con1,con2=alloc(0x140),alloc(0x1e94),alloc(0x1e94)
game,difficulty,settings,flags=alloc(0x3e4),alloc(0x3ac),alloc(0x20),alloc(0x640)
manager,table1,table2=alloc(32),alloc(16),alloc(16)
players=[alloc(0x1e4) for _ in range(5)];ids=[alloc(0x28) for _ in players];nodes=[alloc(32) for _ in range(6)]
iterator,keyptr,scratch=alloc(16),alloc(16),alloc(64)
put(body+0x100,'<I',physics);put(body+0xbc,'<B',0);put(body+0x110,'<B',0)
put(physics+4,'<I',0x5bd63b29);put(physics+12,'<2I',body,0);put(physics+0x1528,'<I',state)
put(physics+0x2ed,'<B',0);put(physics+0x302,'<B',0);put(state+0x28,'<B',0)
put(stats+0x14,'<I',23);put(stats+0x278,'<I',owner);put(owner+0x18,'<I',modifier);put(modifier+0x74,'<B',0)
put(stats+0x280,'<I',physics);put(stats+0x290,'<8f',*range(1,9))
put(network,'<3I',0,con1,con2);put(con1+0x1e84,'<I',8);put(con2+0x1e84,'<I',8)
put(network+0x128,'<I',nodes[0]);put(iterator+4,'<I',network+0x11c)
for i,p in enumerate(players):
    put(p+0x14,'<I',ids[i]);put(p+0x1d0,'<I',0);put(ids[i]+0x14,'<I',[23,24,23,0xffff,0x10017][i])
    put(nodes[i]+4,'<I',p);put(nodes[i]+12,'<I',nodes[i+1])
put(nodes[-1]+4,'<I',0xffffffff);put(nodes[-1]+12,'<I',nodes[-1])
put(game+0x20,'<I',flags);put(game+0x38c,'<I',difficulty);put(game+0x3d0,'<f',0)
put(flags+0x5f0,'<16I',*([0]*16))

default_stat=symbol(0x6357d57c,2,bits(9))
flag_name=0xaaa10001;flag_index=symbol(flag_name,1,33);flag_mapping=symbol(0x6b0f24bc,1,flag_name)
MODE,PARAMETER=0x77770001,0xbabefeed
set_settings,settings_nodes=structure([(0x6dc3d6f1,1,1),(0xa1dc81f9,13,MODE),(0x5a2c589a,1,0)])
put(settings+4,'<2I',0,word(set_settings+4))
difficulty_params,difficulty_nodes=structure([(MODE,1,1),(0x4da4937b,1,2)])
put(difficulty+0x398,'<I',difficulty_params)
basepair,modifierpair,difficultypair=pair(100,200),pair(.4,.8),pair(.5,1.5)
params,paramnodes=structure([(0,5,basepair),(0,1,1),(0x9016b4e7,5,modifierpair),(0xba8fb854,5,difficultypair),(0x8069179f,2,bits(180))])
alternative,alternative_nodes=structure([(0,5,pair(10,30))])
local_set,local_nodes=structure([(PARAMETER,10,params)])
setnames=[0x8cbc89dd,0x8b3b782b,0x05716042,0x8711bc92,0x871ffb73,0x43da544e,0x08c9ad5e,0xd3d12913]
setmodes=[0,0x3029fb1f,0x61c62b2d,0x86929898,0xb2c99bf0,0x906f06e2,0xd8d2d646,0x14a3a4cf]
for i,name in enumerate(setnames):symbol(name,10,local_set if i%2==0 else structure([(PARAMETER,10,alternative)])[0])
symbol(PARAMETER,10,alternative)

# Shared typed/alias/nested graphs, including unnamed checksum inclusions.
numeric=[]
for i,value in enumerate([0,1,-1,2**24+1,-2**24-1,2**31-1,-2**31]):
    name=0xac000001+i;symbol(name,1,value&0xffffffff);numeric.append(name)
float_words=[0,0x80000000,1,0x80000001,0x3fc00000,0xbfc00000,0x4f000000,0x4f800000,0x5effffff,0x5f000000,
    0xdf000000,0xdf000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xffffffff]+[rng.randrange(2**32) for _ in range(240)]
for i,value in enumerate(float_words):
    name=0xad001000+i;symbol(name,2,value);numeric.append(name)
symbol(0xee100001,13,numeric[3]);symbol(0xee100002,13,0xee100001);symbol(0xee100003,13,0xee999999)
numeric += [0xee100001,0xee100002,0xee100003,0,0xffffffff,PARAMETER]
symbol(0xdead1001,5,basepair);symbol(0xdead1002,10,params)
nested,nested_nodes=structure([(0x1111,13,0xee100002),(0x2222,1,15),(0x3333,5,modifierpair),(0x4444,10,alternative)])
symbol(0xdead2001,10,nested);symbol(0xdead2002,13,0xdead2001)
access,access_nodes=structure([(0x1111,1,7),(0,13,0xdead2002),(0x2222,2,bits(5)),(0x3333,13,0xdead1001),
    (0x4444,13,0xdead1002),(0,13,0xee100001),(0,13,0xee999999),(0x1111,13,0xee100003)])

# Two hash tables: colliding chains, zero-valued matches, and secondary fallback.
buckets1,buckets2=alloc(16*12),alloc(16*12);image[buckets1-BASE:buckets1-BASE+16*12]=bytes(16*12)
image[buckets2-BASE:buckets2-BASE+16*12]=bytes(16*12)
put(table1,'<2I',4,buckets1);put(table2,'<2I',4,buckets2);put(manager+8,'<2I',table1,table2)
lookupkeys=[23,39,55,71,24,40,0,0xffffffff,0x10017]
def entry(buckets,key,value):
    slot=buckets+(key&15)*12;at=alloc(12);put(at,'<3I',key,value,word(slot+8));put(slot+8,'<I',at)
for key,value in [(23,body),(39,body),(55,0),(71,body),(0,body),(0xffffffff,body)]:entry(buckets1,key,value)
entry(buckets1,23,0)
for key in [23,55,24,0x10017]:entry(buckets2,key,body)
put(keyptr,'<I',23)
initial=bytes(image[:cursor]);(out/'stats-memory.bin').write_bytes(initial)

pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(0x2000000,0x10000),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
globals_=[('thug_script_symbol_buckets',0x6f3624,BASE),('thug_network_state',0x7cce14,network),
    ('thug_game_settings',0x7ce470,settings),('thug_game_context',0x7ce478,game),('thug_object_lookup_manager',0x6f0fc0,manager)]
for _,at,value in globals_:cpu.mem_write(at,struct.pack('<I',value))
cpu.mem_write(STOP+32,b'\xdd\x1d'+struct.pack('<I',OUTPUT)+b'\xe9'+struct.pack('<i',-43))
functions={}
def bind(address,name,this=True,result='word',cleanup=0):
    functions[hex(address)]={'name':name,'this':this,'result':result,'cleanup':cleanup}
for address,name in [(0x476630,'integer'),(0x476cb0,'boolean'),(0x4767c0,'structure'),(0x476950,'checksum'),(0x476df0,'pair')]:
    bind(address,'thug_script_get_'+name,result='byte',cleanup=12)
bind(0x478f60,'thug_script_get_global_integer',False)
bind(0x47ac00,'thug_script_pair_initialize')
for address,name in [(0x456f90,'connection_flag_8'),(0x44e4f0,'network_is_active'),(0x543320,'player_is_hidden'),
    (0x543490,'player_flag_80'),(0x5433b0,'player_flags_7800'),(0x5651f0,'game_is_multiplayer')]:bind(address,'thug_'+name,result='byte')
bind(0x5a1180,'thug_game_is_split_screen',False,'byte')
bind(0x537010,'thug_player_next',cleanup=8);bind(0x53aea0,'thug_player_find',cleanup=4)
bind(0x553220,'thug_settings_flag',result='byte',cleanup=4)
bind(0x5532a0,'thug_settings_mode');bind(0x553190,'thug_settings_player_count')
bind(0x564d90,'thug_game_difficulty_settings');bind(0x559050,'thug_game_difficulty',cleanup=4)
bind(0x584cc0,'thug_gameplay_flag',result='byte',cleanup=4)
bind(0x462050,'thug_object_table_find',cleanup=8);bind(0x462120,'thug_object_manager_find',cleanup=4)
bind(0x4619f0,'thug_object_find_global',cleanup=4)
for address,name in [(0x580490,'stat'),(0x5805b0,'evaluate_stat_parameter'),(0x580790,'stat_parameter')]:
    bind(address,'thug_skater_'+name,result='double',cleanup=4)
cases=[];counts=Counter();trace=[];coverage=Counter()
def observe(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP);arg=struct.unpack('<I',bytes(uc.mem_read(sp+4,4)))[0]
    trace.append([hex(address),arg]);coverage[hex(address)]+=1
for address in [0x580490,0x5805b0,0x580790,0x478f60,0x584cc0,0x559050,0x553220]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=address,end=address)
def run(fn,this,args=(),patches=(),writes=()):
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
    value=bytes(cpu.mem_read(OUTPUT,8)).hex() if info['result']=='double' else cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff)
    cases.append({'fn':hex(fn),'this':this,'args':list(args),'patches':list(patches),'outputs':outputs,'result':value,
        'flag':cpu.mem_read(0x7ce4fd,1)[0],'trace':list(trace)})
    counts[info['name']]+=1

for name in numeric:
    for assertion in [0,1,256]:run(0x478f60,0,[name,assertion])
for s in [access,nested,params,alternative]:
    for name in [0,0x1111,0x2222,0x3333,0x4444,0x9016b4e7,0xba8fb854,0x8069179f,0xffffffff]:
        for assertion in [0,1,256]:
            for fn in [0x476630,0x476cb0,0x4767c0,0x476950,0x476df0]:run(fn,s,[name,scratch,assertion],writes=[(scratch,16)])
for i in range(64):
    data=bytes(rng.randrange(256) for _ in range(16));run(0x47ac00,scratch,patches=[[scratch,data.hex()]],writes=[(scratch,16)])
# Float loads, NaN quieting, signed zeros and overlapping source/output pairs.
for a in [0,0x80000000,1,0x7f800000,0xff800000,0x7f800001,0xff800001,0x7fc12345,0x80000001]:
    for b in [0,0x80000000,0x7f800001,0xffc12345,0x3f800000]:
        for output in [scratch,basepair,basepair+4,basepair-4]:
            run(0x476df0,params,[0,output,0],[patch(basepair+4,'<2I',a,b)],[(output+4,8)])
for i in range(192):
    f=rng.randrange(2**32);p=[patch(players[0]+0x1d0,'<I',f),patch(con1+0x1e84,'<I',f)]
    for fn,this in [(0x456f90,con1),(0x543320,players[0]),(0x543490,players[0]),(0x5433b0,players[0])]:run(fn,this,patches=p)
for mode in [0,1,4,8,12,255,256]:
    for first in [0,con1]:
        for second in [0,con2]:
            for f1,f2 in [(0,0),(8,0),(0,8),(8,8),(0xffffffff,0xffffffff)]:
                p=[patch(network,'<3I',mode,first,second),patch(con1+0x1e84,'<I',f1),patch(con2+0x1e84,'<I',f2)]
                run(0x44e4f0,network,patches=p)
                for count in [0,1,2,0xffffffff]:
                    q=p+[patch(settings_nodes[0]+8,'<I',count)]
                    run(0x5651f0,game,patches=q);run(0x5a1180,0,[0,0],q)
for variant in range(8):
    p=[]
    if variant==1:p=[patch(players[0]+0x1d0,'<I',4)]
    if variant==2:p=[patch(players[0]+0x1d0,'<I',4),patch(players[1]+0x1d0,'<I',4),patch(players[2]+0x1d0,'<I',4)]
    if variant==3:p=[patch(players[0]+0x14,'<I',0)]
    if variant==4:p=[patch(nodes[0]+4,'<I',0)]
    if variant==5:p=[patch(nodes[2]+4,'<I',0)]
    if variant==6:p=[patch(network+0x128,'<I',nodes[-1])]
    if variant==7:p=[patch(players[0]+0x1d0,'<I',4),patch(nodes[1]+4,'<I',0)]
    for name in [0,23,24,25,0xffff,0x10017,0xffffffff]:run(0x53aea0,network,[name],p)
    for start in [network+0x11c]+nodes[:-1]:
        for include in [0,1,256,257]:run(0x537010,network,[iterator,include],p+[patch(iterator+4,'<I',start)],[(iterator,8)])
for variant in range(8):
    p=[patch(settings_nodes[0]+8,'<I',[0,1,2,0xffffffff,3,0,0,0][variant])]
    if variant==5:p+=[patch(settings_nodes[0],'<B',4)]
    if variant==6:p+=[patch(settings+8,'<I',0)]
    if variant==7:p+=[patch(settings_nodes[0],'<B',26),patch(settings_nodes[0]+8,'<I',numeric[3])]
    for fn in [0x553190,0x5532a0]:run(fn,settings,patches=p)
    for name in [0x6dc3d6f1,0xa1dc81f9,0x5a2c589a,0xffffffff]:run(0x553220,settings,[name],p)
for value in [0,1,2,3,0xffffffff,0x80000000]:
    for force in [0,1,256,257]:
        for present in [0,1]:
            p=[patch(difficulty_nodes[0]+8,'<I',value),patch(difficulty_nodes[1]+8,'<I',2-value if value<=2 else value)]
            if not present:p+=[patch(difficulty_params+4,'<I',0)]
            run(0x559050,difficulty,[force],p)
run(0x564d90,game)
for index in [0,1,31,32,33,63,64,127,255,-1,-32,-33]:
    for f in [0,1,0x80000000,0xffffffff,0xaaaaaaaa]:
        p=[patch(flag_index+12,'<I',index&0xffffffff),patch(flags+0x5f0+(index>>5)*4,'<I',f)]
        run(0x584cc0,flags,[flag_name],p)
for key in lookupkeys+[rng.randrange(2**32) for _ in range(48)]:
    for shift in [4,36]:
        p=[patch(keyptr,'<I',key),patch(table1,'<I',shift),patch(table2,'<I',shift)]
        for table in [table1,table2]:run(0x462050,table,[keyptr,1],p)
        run(0x462120,manager,[key],p);run(0x4619f0,0xdeadbeef,[key],p)
for table in [table1,table2]:run(0x462050,table,[keyptr,0],[patch(table,'<2I',32,0)])

# Full stat getter: offline, split screen, network overrides, hidden/missing
# players, global fallback, the double checksum lookup, and the final +3.
statwords=[bits(x) for x in [-1,0,-0.,1,3,6,10,15,100,2**24]]+[1,0x80000001,0x7f7fffff,0x7f800000,0x7fc12345]
for i in range(2048):
    index=i%8;v=rng.choice(statwords);override=rng.choice([0,0x80000000,0,bits(7),0x7fc12345])
    p=[patch(stats+0x290+4*index,'<I',v),patch(game+0x3d0,'<I',override),patch(modifier+0x74,'<B',(i//8)%2),
        patch(network,'<I',[0,4,8,12][(i//16)%4]),patch(con1+0x1e84,'<I',rng.choice([0,8])),
        patch(settings_nodes[0]+8,'<I',rng.choice([0,1,2,0xffffffff])),patch(players[0]+0x1d0,'<I',rng.choice([0,4,128,0x800,0x7880])),
        patch(stats+0x14,'<I',rng.choice([23,24,25,0x10017])),patch(flags+0x5f4,'<I',2 if i%7==0 else 0),
        patch(default_stat+1,'<B',1 if i%3==0 else 2),patch(default_stat+12,'<I',16777217 if i%3==0 else bits(8.75))]
    run(0x580490,stats,[index],p)
    assert [t[1] for t in trace if t[0]=='0x478f60']==[0x6b0f24bc,flag_name]
    assert sum(t[0]=='0x584cc0' for t in trace)==1

# Formula ordering, modifier gating/clamping, difficulty scaling and limit direction.
# Include subnormals, wide intermediates, NaNs and infinities, with float stores
# at the same boundaries as the executable. Numeric NaNs compare by classification.
pair_values=[(100,200),(200,100),(100,100),(0,0),(-100,100),(1e-40,2e-40),(1e35,-1e35),
    (float('nan'),10),(10,float('nan')),(float('inf'),1),(-float('inf'),float('inf'))]
mod_values=[(.4,.8),(-4,-2),(2,4),(1,1),(0,0),(float('nan'),1),(1e-40,2e-40)]
for i in range(4096):
    low,high=pair_values[i%len(pair_values)];mx,my=mod_values[(i//len(pair_values))%len(mod_values)]
    p=[patch(basepair+4,'<2f',low,high),patch(modifierpair+4,'<2f',mx,my),
        patch(stats+0x290,'<8f',*[rng.uniform(-10,20) for _ in range(8)]),
        patch(difficultypair+4,'<2f',rng.choice([.1,.5,0,1,2]),rng.choice([1,1.5,2,0,-1])),
        patch(paramnodes[1]+8,'<I',i%8),patch(paramnodes[4]+8,'<f',rng.choice([0,50,150,500,float('nan')])),
        patch(body+0x110,'<B',rng.choice([0,1,255])),patch(state+0x28,'<B',rng.choice([0,1,128])),
        patch(difficulty_nodes[0]+8,'<I',(i//8)%4),patch(settings_nodes[2]+8,'<I',(i//32)%2),
        patch(modifier+0x74,'<B',(i//64)%2),patch(settings_nodes[0]+8,'<I',1)]
    # Hide optional members by changing their type to an unrelated string type.
    for n,divisor in [(0,5),(1,7),(2,11),(3,13),(4,17)]:
        if i%divisor==0:p.append(patch(paramnodes[n],'<B',6))
    run(0x5805b0,stats,[params],p)
    assert sum(t[0]=='0x559050' for t in trace)==1 and sum(t[0]=='0x553220' for t in trace)==1
    if i%1024==0:print(i,'stat formula comparisons',flush=True)
for i in range(512):
    p=[patch(stats+0x14,'<I',lookupkeys[i%len(lookupkeys)]),patch(body+0xbc,'<B',i%2),
        patch(physics+0x2ed,'<B',(i//2)%2),patch(physics+0x2f0,'<I',setmodes[(i//4)%len(setmodes)]),
        patch(physics+0x302,'<B',(i//32)%2),patch(local_nodes[0],'<B',20 if i%3 else 2),
        patch(difficulty_nodes[0]+8,'<I',(i//64)%3),patch(flags+0x5f4,'<I',2 if i%7==0 else 0)]
    run(0x580790,stats,[PARAMETER],p)
    assert sum(t[0]=='0x5805b0' for t in trace)==1

fixture={'base':BASE,'memory':'stats-memory.bin','globals':globals_,'functions':functions,'cases':cases}
path=out/'stats-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_stats_wasm.mjs'),str(out)],check=True)
wasm_report=json.loads((out.parent/'stats-wasm.json').read_text())
report={'result':'pass','specimen_sha256':SHA256,'cases':len(cases),'counts':dict(counts),'original_call_observations':dict(coverage),
    'scope':'Complete stat getter, evaluator and named lookup with real x86 callees on constructed script/object/player graphs; not a loaded game or full movement loop.',
    'x87_control_word':'0x007f','runtime_control_word_observed_in_game':False,
    'nan_fields_classification_only':wasm_report['nan_fields_classification_only'],
    'pair_nan_quieting_checks':wasm_report['pair_nan_quieting_checks'],
    'pair_nan_documented_oracle_differences':wasm_report['pair_nan_documented_oracle_differences'],
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'stats-memory.bin']},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',len(cases),'cases;',len(functions),'original functions; report:',report_path)
