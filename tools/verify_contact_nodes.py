"""Original collision identity and node lookup dependencies, without call stubs.

Constructed, acyclic script graphs and terminated node tables. The complete
collision-event dispatcher and script execution are not covered by this suite.
"""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load

out=ROOT/'local/validation/collision';report_path=out.parent/'contact-nodes.json'
report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP=0x1800000,0x40000,0x3000000,0x3f00000
memory=bytearray(0x4000);rng=random.Random(0x434bf0)
def alloc(size):
    at=BASE+len(memory);memory.extend(b'\xad'*((size+3)&~3));assert len(memory)<SIZE;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def word(at):return struct.unpack_from('<I',memory,at-BASE)[0]
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def structure(entries):
    at=alloc(8);nodes=[alloc(16) for _ in entries];put(at,'<2I',0,nodes[0] if nodes else 0)
    for i,(name,kind,value) in enumerate(entries):
        put(nodes[i],'<4I',kind*2+(i&1),name,value,nodes[i+1] if i+1<len(nodes) else 0)
    return at,nodes
def symbol(name,kind,value):
    at=alloc(20);bucket=BASE+(name&4095)*4
    put(at,'<BBHIIII',0,kind,0,name,0,value,word(bucket));put(bucket,'<I',at)

NAME,FLAG=0xa1dc81f9,0x68910ac6
empty,_=structure([])
leaf,leaf_nodes=structure([(0,13,FLAG),(NAME,13,0x11223344)])
symbol(0xdead1001,10,leaf);symbol(0xdead1002,13,0xdead1001)
symbol(0xdead1003,13,0xdead1002);symbol(0xdead1004,13,0xfaceeeee)
symbol(0xdead1005,1,FLAG);symbol(0,10,leaf)
outer,outer_nodes=structure([(0,13,0xdead1003),(NAME,13,0x55667788)])
symbol(0xdead1006,10,outer)
access,access_nodes=structure([(0,13,0xdead1006),(0,13,0),(17,13,FLAG),(0,1,FLAG)])
single,single_nodes=structure([(0,13,FLAG)])
names,name_nodes=structure([(NAME,13,1),(0,13,0xdead1006),(NAME,13,3)])

network,con1,con2,settings=alloc(0x140),alloc(0x1e88),alloc(0x1e88),alloc(12)
settings_struct,settings_nodes=structure([(0x6dc3d6f1,1,1)])
put(settings+4,'<2I',0,word(settings_struct+4));put(network,'<3I',0,con1,con2)
put(con1+0x1e84,'<I',8);put(con2+0x1e84,'<I',8)

table=alloc(0x10004+12*6)
for i in range(16384):put(table+i*4,'<Hh',0xadad,-1)
node_structs=[];node_members=[]
for i in range(6):
    s,n=structure([(NAME,13,i+1)]);node_structs.append(s);node_members.append(n[0])
arrays=[]
for i in range(6):
    array,items=alloc(12),alloc(32);arrays.append(array)
    for j in range(8):put(items+j*4,'<I',node_structs[(i+j)%6])
    # A shifted base permits valid reads at indices -2 through 5.
    put(array,'<3I',0xface,8,items+8)
    put(table+0x1000c+12*i,'<I',array)
inline=alloc(12);put(inline,'<3I',0xaaaa,1,node_structs[4])
probe=alloc(0xb0)
initial=bytes(memory);(out/'contact-nodes-memory.bin').write_bytes(initial)
globals_=[['thug_script_symbol_buckets',0x6f3624,BASE],['thug_network_state',0x7cce14,network],
    ['thug_game_settings',0x7ce470,settings],['thug_node_table',0x6f0d84,table]]
functions={}
def bind(at,name,this=True,result='word',cleanup=0):
    functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':cleanup}
bind(0x45c1b0,'thug_node_find',False)
bind(0x45cfc0,'thug_node_table_find',cleanup=8)
bind(0x45be40,'thug_node_name',False)
bind(0x46cc30,'thug_script_array_structure',cleanup=4)
bind(0x476b40,'thug_script_has_flag',result='byte',cleanup=4)
bind(0x565bb0,'thug_script_multiplayer_gate',False,cleanup=4)
bind(0x417140,'thug_collision_probe_event_object')
bind(0x417210,'thug_collision_probe_has_moving_object',result='byte')
bind(0x417240,'thug_collision_probe_moving_object')

pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
for _,at,value in globals_:cpu.mem_write(at,struct.pack('<I',value))
cases=[];counts=Counter();coverage=Counter();events=Counter()
def observe(uc,address,size,user):events[hex(address)]+=1;coverage[hex(address)]+=1
for at in [0x45cfc0,0x46cc30,0x476950,0x476b40,0x478cf0,0x44e4f0,0x553190]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)
def run(fn,this=0,args=(),patches=(),writes=()):
    info=functions[hex(fn)];expected=bytearray(initial)
    for at,data in patches:
        raw=bytes.fromhex(data);expected[at-BASE:at-BASE+len(raw)]=raw
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x7ce4fd,b'\xad');cpu.mem_write(0,b'\xa5'*4)
    sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP,*[v&0xffffffff for v in args]))
    cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad)
    events.clear();cpu.emu_start(fn,STOP,count=200000)
    assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+info['cleanup'],hex(fn)
    assert bytes(cpu.mem_read(0,4))==b'\xa5'*4
    after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
    for at,length in writes:
        data=after[at-BASE:at-BASE+length];expected[at-BASE:at-BASE+length]=data;outputs.append([at,data.hex()])
    assert after==expected,('unexpected write',hex(fn))
    result=cpu.reg_read(UC_X86_REG_EAX)&(255 if info['result']=='byte' else 0xffffffff)
    cases.append({'fn':hex(fn),'this':this,'args':[v&0xffffffff for v in args],'patches':list(patches),
        'outputs':outputs,'result':result,'flag':cpu.mem_read(0x7ce4fd,1)[0],'events':dict(events)})
    counts[info['name']]+=1
    return result

# Flag storage types, named members, aliases, recursive inclusions and literals.
for kind in range(256):
    for member_name in [0,17]:
        p=[patch(single_nodes[0],'<B',kind),patch(single_nodes[0]+4,'<I',member_name)]
        assert run(0x476b40,single,[FLAG],p)==int(not member_name and kind in (26,27))
for s in [empty,leaf,outer,access,single,names]:
    for flag in [0,FLAG,0xdead1001,0xdead1002,0xdead1003,0xdead1004,0xdead1005,0xdead1006,17,0xffffffff]:
        run(0x476b40,s,[flag])
for value in [0,FLAG,0xdead1001,0xdead1002,0xdead1003,0xdead1004,0xdead1005,0xffffffff]:
    p=[patch(single_nodes[0]+8,'<I',value)]
    # Literal equality wins even if the value resolves to a structure or alias.
    assert run(0x476b40,single,[value],p)==1
    run(0x476b40,single,[FLAG],p)
# A successful early match must not walk the deliberately invalid next link.
assert run(0x476b40,single,[FLAG],[patch(single_nodes[0]+12,'<I',0xdeadbeef)])==1

# Exact last-match/nested checksum semantics and missing-name defaults.
for s in [empty,leaf,outer,access,single,names,*node_structs]:run(0x45be40,args=[s])
for kind in range(256):
    run(0x45be40,args=[names],patches=[patch(name_nodes[-1],'<B',kind)])

# Inline storage ignores the index. Other counts use it, including signed reads.
for index in [0,1,-1,-2,32767,-32768,0x7fffffff,0x80000000,0xffffffff]:
    assert run(0x46cc30,inline,[index])==node_structs[4]
for array in arrays:
    for count in [0,2,8,0xffffffff]:
        for index in range(-2,6):run(0x46cc30,array,[index],[patch(array+4,'<I',count)])

# Build isolated collision chains, including wrap from slot 16383 to zero.
for start in [0,1,16382,16383,348,4095]:
    for length in range(7):
        p=[];keys=[]
        for i in range(length):
            key=((i+1)<<14)|start;keys.append(key)
            # Index -2 picks group i's first item. The single item alternative
            # uses a large positive index, intentionally ignored by the getter.
            p += [patch(table+((start+i)&16383)*4,'<Hh',i,-2),patch(node_members[i]+8,'<I',key)]
        for key in keys+[0xabcd0000|start]:
            for fn in [0x45cfc0,0x45c1b0]:
                result=run(fn,table,[key,rng.randrange(2**32)],p)
                assert result==(node_structs[keys.index(key)] if key in keys else 0)
# One-item slot, missing name resolving to zero, and duplicate-name first hit.
p=[patch(table+7*4,'<Hh',5,32767),patch(table+0x1000c+12*5,'<I',inline),patch(node_members[4]+8,'<I',7)]
for fn in [0x45cfc0,0x45c1b0]:assert run(fn,table,[7,0],p)==node_structs[4]
p=[patch(table,'<Hh',0,-2),patch(node_structs[0]+4,'<I',0)]
for fn in [0x45cfc0,0x45c1b0]:assert run(fn,table,[0,1],p)==node_structs[0]
p=[patch(table,'<HhHh',0,-2,1,-2),patch(node_members[0]+8,'<I',0),patch(node_members[1]+8,'<I',0)]
for fn in [0x45cfc0,0x45c1b0]:assert run(fn,table,[0,1],p)==node_structs[0]

# Flag gate short-circuiting, both connections, unsigned count and missing count.
for i in range(384):
    s=[empty,single,outer,access][i%4]
    nf=[0,4,8,12,1,0xffffffff][i%6];count=[0,1,2,0xffffffff,0x80000000,17][(i//6)%6]
    c1=con1 if i&8 else 0;c2=con2 if i&16 else 0
    p=[patch(network,'<3I',nf,c1,c2),patch(con1+0x1e84,'<I',8 if i&32 else 0),
       patch(con2+0x1e84,'<I',8 if i&64 else 0),patch(settings_nodes[0]+8,'<I',count)]
    if i%13==0:p.append(patch(settings+8,'<I',0))
    run(0x565bb0,args=[s],patches=p)
    if s==empty:assert not events['0x44e4f0'] and not events['0x553190']
    if events['0x553190']:assert events['0x44e4f0']

# Only the stale-id predicate writes; random poison detects unintended clears.
for i in range(256):
    raw=bytes(rng.randrange(256) for _ in range(0xb0))
    owner=[0,0x12345678,0xffffffff,probe][i%4];old_id=[0,1,0xffffffff][(i//4)%3]
    p=[[probe,raw.hex()],patch(probe+0x98,'<I',owner),patch(probe+0xa4,'<I',old_id)]
    for fn in [0x417140,0x417240]:run(fn,probe,patches=p)
    assert run(0x417210,probe,patches=p,writes=[(probe+0xa4,4),(probe+0x58,4)])==int(bool(owner))

scope='Original node table lookup, script arrays and unnamed flags, multiplayer event gate and collision owner accessors. Real unmodified callees; constructed graphs and probe states. No node loader, collision-event dispatcher or script execution.'
fixture={'base':BASE,'memory':'contact-nodes-memory.bin','globals':globals_,'functions':functions,
    'cases':cases,'float_ranges':[],'coverage':dict(coverage),'scope':scope}
path=out/'contact-nodes-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',dict(counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_contact_nodes_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'scope':scope,
    'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
    'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'contact-nodes-memory.bin']},
    'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
