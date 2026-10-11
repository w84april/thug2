"""Complete native Kill and its class handler against original instructions.
The constructed node/prefix indexes are fixture state, not a recovered loader.
"""
from pathlib import Path
exec(compile(Path('local/analysis/scene-lifetime-fixture-setup.py').read_text(),'<lifetime fixture>','exec'))
import itertools
from unicorn.x86_const import UC_X86_REG_EIP
old_size=SIZE;SIZE=0x100000
oracle.cpu.mem_map(BASE+old_size,SIZE-old_size)
memory.extend(b'\xad'*(SIZE-old_size));put(CONTEXT+20,'<I',BASE+SIZE)
NODETABLE,GAME,NET,SETTINGS,PREFIX,SCENES,RAILS,EMITTERS= [BASE+x for x in [0x80000,0x91000,0x91400,0x91600,0x91800,0x91900,0x91a00,0x91b00]]
memory[NODETABLE-BASE:NODETABLE-BASE+0x10000]=b'\x00\x00\xff\xff'*16384
for p,n in [(GAME,0x400),(NET,0x200),(SETTINGS,0x100),(PREFIX,0x100),(SCENES,0x100),(RAILS,0x100),(EMITTERS,0x100)]:memory[p-BASE:p-BASE+n]=bytes(n)
put(GAME+0x24,'<I',RAILS);put(GAME+0x28,'<4I',0,0xffffffff,0,GAME+0x28)
put(SCENES,'<4I',0,0xffffffff,0,SCENES)
put(EMITTERS,'<6I',2,EMITTERS+32,0,0xffffffff,0,0)
initial=bytes(memory);oracle.initial=initial
for name,at,value in [('thug_node_table',0x6f0d84,NODETABLE),('thug_game_context',0x7ce478,GAME),
 ('thug_network_state',0x7cce14,NET),('thug_game_settings',0x7ce470,SETTINGS),
 ('thug_node_prefix_manager_draft',0x6f0d80,PREFIX),('thug_collision_scene_list',0x6fa7ec,SCENES),
 ('thug_emitter_table_draft',0x6f2260,EMITTERS),('thug_proximity_manager_draft',0x6f2268,0),
 ('thug_aux_geometry_count_draft',0x787350,0),('thug_scene_light_count_draft',0x6faef0,0),
 ('thug_decal_light_count',0x6faef4,0)]:
    if at in index:defaults[index[at]]=value
    else:glob(name,at,value)
for name,at,size in [('thug_aux_geometry_draft',0x787360,8*0x58),('thug_scene_lights_draft',0x6faaf0,16*4),
 ('thug_decal_lights',0x6faf80,8*36),('thug_node_prefix_results_draft',0x6efde0,1000*4)]:
    for off in range(0,size,4):glob(name,at+off,0,4,off)
# Pure qualification data read by the shared dispatcher, eliminated for Kill.
# It is immutable in every case; original-only because no Kill state depends on it.
oracle.setword(0x701378,2)
for a,n,name,argc in [(0x4d8c90,39,'thug_aux_geometry_set_enabled_draft',2),
 (0x4b22f0,5,'thug_aux_geometry_set_enabled_forward_draft',2),
 (0x48bf90,5,'thug_scene_aux_geometry_set_enabled_draft',2),
 (0x5a32c0,528,'thug_scene_kill_named_draft',2),(0x5a5030,21,'thug_script_kill_draft',2)]:
    bind_new(a,n,name,argc,'byte' if a in [0x5a32c0,0x5a5030] else 'void',this=False)
for a in [0x5a4ef0,0x5a4da0,0x45c1b0,0x565bb0,0x476ba0,0x49cb00,0x49e9b0,0x48bf90,0x5665c0,0x55d990]:
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
shared={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x5a4ef0,243),(0x5a4da0,301)]}
shared_hits=Counter()
for a,code in shared.items():oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:shared_hits.update([at]),begin=a,end=code[-1].address)

# Reuse the already pinned, explicitly test-only renderer argument witness.
VT,CBLOG,CBCONTROL,CB=BASE+0x5200,BASE+0x5000,BASE+0x5100,oracle.stop+0x200
def renderer(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);receiver=cpu.reg_read(UC_X86_REG_ECX);enabled=oracle.word(sp+4)
    watch,write=oracle.word(CBCONTROL),oracle.word(CBCONTROL+4)
    oracle.setword(CBLOG,oracle.word(CBLOG)+1);oracle.setword(CBLOG+4,receiver);oracle.setword(CBLOG+8,enabled)
    oracle.setword(CBLOG+12,oracle.word(watch) if watch else 0x13579bdf)
    if write:oracle.setword(write,oracle.word(CBCONTROL+8))
    cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+8)
oracle.cpu.hook_add(UC_HOOK_CODE,renderer,begin=CB,end=CB)
extra.update({'native_callbacks':[{'module':'scene-state-callback.wasm','export':'fixture_scene_enabled','slots':[VT+0x34]}],
 'callback_counter':'renderer_dispatches','oracle_only_read_state':{'0x701378':2}})
class Graph:
    def __init__(self):
        self.image=bytearray(initial);self.cursor=BASE+0x92000
        self.put(VT+0x34,'<I',CB);self.put(CBLOG,'<4I',0,0,0,0);self.put(CBCONTROL,'<3I',0,0,0)
        self.put(SCRIPTS+0xbc,'<I',0)
        component=self.alloc(16);self.put(component,'<4I',2,0x6dc3d6f1,1,0)
        self.put(SETTINGS+4,'<2I',0,component)
    def put(self,p,fmt,*values):struct.pack_into(fmt,self.image,p-BASE,*values)
    def word(self,p):return struct.unpack_from('<I',self.image,p-BASE)[0]
    def alloc(self,n):
        p=self.cursor;self.cursor=(p+n+19)&~3;assert self.cursor<BASE+SIZE;return p
    def text(self,s):
        s=s.encode()+b'\0';p=self.alloc(len(s));self.image[p-BASE:p-BASE+len(s)]=s;return p
    def structure(self,items):
        p=self.alloc(8);nodes=[self.alloc(16) for _ in items];self.put(p,'<2I',0,nodes[0] if nodes else 0)
        for i,(name,kind,value) in enumerate(items):self.put(nodes[i],'<4I',kind*2,name,value,nodes[i+1] if i+1<len(nodes) else 0)
        return p
    def array(self,kind,values):
        p=self.alloc(12);self.put(p,'<BBHII',0,kind,0,len(values),0)
        if len(values)==1:self.put(p+8,'<I',values[0])
        elif values:
            items=self.alloc(len(values)*4);self.put(items,'<'+'I'*len(values),*values);self.put(p+8,'<I',items)
        return p
    def symbol(self,name,kind,value):
        p=self.alloc(20);bucket=SYMBOLS+(name&4095)*4
        self.put(p,'<BBH4I',0,kind,0,name,0,value,self.word(bucket));self.put(bucket,'<I',p)
    def table(self,entries):
        t=self.alloc(24);b=self.alloc(48);self.put(t,'<6I',2,b,len(entries),0xffffffff,0,0)
        for i in range(4):self.put(b+i*12,'<3I',0,0,0)
        for name,value in entries:
            head=b+(name&3)*12
            if self.word(head+4):
                tail=self.alloc(12);self.put(tail,'<3I',name,value,self.word(head+8));self.put(head+8,'<I',tail)
            else:self.put(head,'<3I',name,value,0)
        return t
    def nodes(self,specs):
        result=[]
        for key,kind,flags in specs:
            items=[] if key is None else [(0xa1dc81f9,13,key)]
            if kind is not None:items.append((0x12b4e660,13,kind))
            result.append(self.structure(items+[(0,13,flag) for flag in flags]))
        a=self.array(10,result);self.put(NODETABLE+0x10004,'<3I',0,0,a)
        for i,(key,_,_) in enumerate(specs):
            slot=(key or 0)&0x3fff
            while self.word(NODETABLE+slot*4)>>16!=0xffff:slot=(slot+1)&0x3fff
            self.put(NODETABLE+slot*4,'<HH',0,i)
        return a,result
    def prefix(self,key,array,indices,next_=0):
        count=len(indices);values=self.alloc(max(count*2,2))
        if count:self.put(values,'<'+'H'*count,*indices)
        found=self.alloc(8);self.put(found,'<HHI',count,0x1357,values)
        name=0x55000000+(self.cursor&0xffff);self.symbol(name,12,array)
        entry=self.alloc(12);self.put(entry,'<3I',self.table([(key,found)]),name,next_)
        self.put(PREFIX,'<I',entry);return entry
    def patches(self):
        result=[]
        for page in range(0,SIZE,4096):
            if self.image[page:page+4096]!=initial[page:page+4096]:
                for i in range(page,page+4096,4):
                    if self.image[i:i+4]!=initial[i:i+4]:result.append([BASE+i,self.image[i:i+4].hex()])
        return result
def run(g,calls,label,changes=None,p=()):
    before_aux=oracle.coverage['0x48bf90']
    stages=case(calls,g.patches()+list(p),changes,label)
    previous=0
    for s in stages:
        for at,data in s['outputs']:
            if at==CBLOG:
                now=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=now-previous;previous=now
    return stages,oracle.coverage['0x48bf90']-before_aux
def named(key):return call(0x5a32c0,args=[key,SCRIPTS])
def native(params,script=SCRIPTS):return call(0x5a5030,args=[params,script])
def aux(count,key):
    change={0x787350:count}
    for i in range(8):
        for j in range(22):change[0x787360+i*0x58+j*4]=0xa5000000+i*32+j
        change[0x787360+i*0x58+4]=key if i%3!=1 else key^0x100
    return change
KEY=0x12345678;crc=lambda s:zlib.crc32(s.lower().encode())^0xffffffff
for count,value in itertools.product([0,1,8],[0,1,255,256,257,0xffffffff]):
    g=Graph();run(g,[call(a,args=[KEY,value]) for a in [0x4d8c90,0x4b22f0,0x48bf90]],f'aux count{count},byte{value:x}',aux(count,KEY))
for kind in [None,0,1,0x30c19601,0x8e6b02ac,0xa0dfac97,0xa0e52803,0xbf4d3537,0xe47f1b78,0xffffffff]:
    g=Graph();g.nodes([(KEY,kind,[])])
    stages,_=run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],f'unrecognized class {kind}')
    assert [s['result'] for s in stages]==[0,0]
g=Graph();run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],'absent node')
for kind,whole,found in itertools.product([0x30c19600,0x8e6b02ad],[False,True],[False,True]):
    g=Graph();g.nodes([(KEY,kind,[crc('FLAG_WHOLE_RAIL')] if whole else [])]);nodes=g.alloc(3*0x54)
    for i in range(3):g.put(nodes+i*0x54+0x40,'<4I',nodes+(i+1)*0x54 if i<2 else 0,0,0xff,KEY if found and i==0 else KEY+1)
    g.put(RAILS+0x40,'<3I',nodes,0,3)
    stages,_=run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],f'rail class{kind:x},whole{whole},found{found}')
    assert all(s['result']==1 for s in stages)
    assert oracle.word(nodes+0x48)==(0xfb if found else 0xff)
    assert oracle.word(nodes+0x54+0x48)==(0xfb if found and whole else 0xff)
for kind in [0x061a741e,0x5b8ab877,0x9e7d469e,0xa0dfac98,0xb7b3bd86,0xe47f1b79,0xef59c100]:
  for flags in [0,2]:
    g=Graph();g.nodes([(KEY,kind,[])]);p=[];calls=[]
    for i in range(3):
        p+=ready_object(i,flags if i==1 else 0)+[patch(OBJ+i*512+0x14,'<I',KEY if i<2 else KEY+1)]
        calls.append(call(0x461a00,MANAGER,[OBJ+i*512]))
    stages,_=run(g,calls+[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],f'generic class{kind:x},flags{flags}',p=p)
    assert all(s['result']==1 for s in stages[-2:])
    assert oracle.word(OBJ+0xc)==0 and oracle.word(OBJ+512+0xc)==(MANAGER if flags&2 else 0)
    assert oracle.word(OBJ+1024+0xc)==MANAGER
for shape in ['empty','missing','first','second','duplicate']:
    g=Graph();g.nodes([(KEY,0xd64dc7c2,[])]);emitters=[g.alloc(0x28) for _ in range(2)]
    for i,p in enumerate(emitters):g.put(p,'<I',KEY if shape=='duplicate' or shape==['first','second'][i] else KEY+1);g.put(p+0x24,'<I',0xff)
    table=g.table([] if shape=='empty' else [(1,emitters[0]),(5,emitters[1])]);changes={0x6f2260:table}
    run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],'emitter '+shape,changes)
for n in [0,1,3]:
    g=Graph();g.nodes([(KEY,0xa0e52802,[])]);changes={0x6faef0:n,0x6faef4:n}
    for i in range(n):
        light=g.alloc(0x30);g.put(light+0x28,'<I',KEY if i!=1 else KEY+1);changes[0x6faaf0+4*i]=light
        table=g.table([(1,0x1234)]);changes[0x6faf80+i*36+24]=KEY if i!=1 else KEY+1;changes[0x6faf80+i*36+32]=table
    run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],'light actual destruction '+str(n),changes)
for count,found,render,flag in [(0,-1,0,0),(2,-1,0,0),(2,0,0,0),(2,1,1,0),(2,0,1,1),(2,0,1,0)]:
    g=Graph();g.nodes([(KEY,0xbf4d3536,[0x4e549fe1] if flag else [])]);entry=SCENES
    for i in range(count):
        next_=g.alloc(16);scene=g.alloc(0xd8);geometry=g.alloc(0x20);collision=g.alloc(0x10);receiver=g.alloc(8)
        g.put(collision+8,'<I',0x12345680);g.put(receiver,'<I',VT)
        g.put(geometry+0x14,'<2I',receiver if render else 0,collision)
        g.put(CBCONTROL,'<3I',collision+8,0,0)
        g.put(scene+0xd0,'<I',g.table([(KEY if i==found else KEY+1,geometry)]))
        g.put(entry,'<4I',0,scene,0,next_);entry=next_
    g.put(entry,'<4I',0,0xffffffff,0,entry)
    stages,auxcalls=run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],f'geometry count{count},found{found},render{render},flag{flag}',aux(8,KEY))
    assert all(s['result']==1 for s in stages) and auxcalls==2*(1+flag)
g=Graph();g.nodes([(None,0xbf4d3536,[])])
stages,auxcalls=run(g,[named(0)],'geometry missing Name retains auxiliary state',aux(8,0));assert stages[0]['result']==1 and auxcalls==0
for active,found in itertools.product([0,1],[False,True]):
    g=Graph();g.nodes([(KEY,0x08470f2e,[])]);pm=g.alloc(8);pn=g.alloc(0xa8)
    g.put(pm,'<2I',pn,0);g.put(pn,'<I',KEY if found else KEY+1);g.put(pn+0x54,'<5I',active,0,0,0,0xabcdef01);g.put(pn+0xa0,'<2I',0,0)
    run(g,[named(KEY),native(g.structure([(0xa1dc81f9,13,KEY)]))],f'proximity active{active},found{found}',{0x6f2268:pm})

# Selection and filtering, including original pure owner-list qualification.
for flags,connection,players,nodeflag,owner in itertools.product([0,4,8,12],[False,True],[1,2],[False,True],[False,True]):
    g=Graph();g.nodes([(KEY,0x30c19600,[0x68910ac6] if nodeflag else [])]);g.put(NET,'<I',flags)
    if connection:
        c=g.alloc(0x1e88);g.put(c+0x1e84,'<I',0);g.put(NET+4,'<I',c)
    g.put(g.word(SETTINGS+8)+8,'<I',players)
    if owner:
        a=g.alloc(16);b=g.alloc(16);g.put(GAME+0x34,'<I',a);g.put(a,'<4I',0,OBJ,0,b);g.put(b,'<4I',0,OBJ+512,0,GAME+0x28);g.put(SCRIPTS+0xbc,'<I',OBJ+512)
    stages,_=run(g,[native(g.structure([(0xa1dc81f9,13,KEY)]))],f'network{flags},connection{connection},players{players},flag{nodeflag},owner{owner}')
    assert stages[0]['result']==(0 if flags&12 and nodeflag and (connection or players>1) else 1)
for selection in ['empty','wrong type','name checksum','name text','prefix checksum','prefix text','prefix empty','prefix overrides name','prefix wrong fallback','links','second flag','both flags','prefix flag']:
    g=Graph();key=crc('target');prefix_key=crc('target_');array,_=g.nodes([(key,0x30c19600,[]),(key+0x4000,None,[])])
    if selection!='prefix empty':g.prefix(prefix_key,array,[1,0,1,0])
    items=[]
    if selection in ['name checksum','prefix wrong fallback']:items=[(0xa1dc81f9,13,key)]
    if selection=='name text':items=[(0xa1dc81f9,3,g.text('TARGET'))]
    if selection.startswith('prefix') and selection!='prefix wrong fallback':items=[(0x6c4e7971,3 if selection=='prefix text' else 13,g.text('TARGET_') if selection=='prefix text' else prefix_key)]
    if selection=='prefix overrides name':items.append((0xa1dc81f9,13,0xdeadbeef))
    if selection=='prefix wrong fallback':items.append((0x6c4e7971,1,0))
    if selection=='wrong type':items=[(0xa1dc81f9,1,key)]
    if selection in ['links','both flags']:items.append((0,13,0x2e7d5ee7))
    if selection in ['second flag','both flags']:items.append((0,13,0xbceb479a))
    if selection=='prefix flag':items.append((0,13,0x80804991))
    stages,_=run(g,[native(g.structure(items),0)],selection)
    assert stages[0]['result']==(0 if selection in ['empty','wrong type'] else 1)
# Prefix-selected generic objects really unregister and destroy; duplicate names
# remain in the live result buffer and safely perform a subsequent empty visit.
g=Graph();a,_=g.nodes([(KEY,0x061a741e,[]),(KEY+1,0x061a741e,[])]);g.prefix(7,a,[1,0,1]);p=[];calls=[]
for i in range(2):p+=ready_object(i)+[patch(OBJ+i*512+0x14,'<I',KEY+i)];calls.append(call(0x461a00,MANAGER,[OBJ+i*512]))
run(g,calls+[native(g.structure([(0x6c4e7971,13,7)]))],'prefix actual object removal in returned order',p=p)
assert all(oracle.word(OBJ+i*512+0xc)==0 for i in range(2))
scope='Five complete original entry points: auxiliary enabled setter and two jump wrappers, class-specific Kill5a32c0, and native Kill5a5030 with constant operation1 specialization of shared selectors. Actual node/prefix lookups, rail/proximity/emitter/light changes, scene lookup/collision changes, object traversal/destruction and multiplayer gates execute; the renderer virtual call uses an explicitly test-only argument/state witness. Constructed indexes are valid fixture data, not recovered production loading. Name/text/prefix precedence, empty-prefix success, ignored prefix per-node failures, early flags and retained deletion compare against full1MiB arena, watched globals and heap effects. Pure shared owner qualification reads are dead for operation1; original-only701378=2 exercises both owner matches. No other shared operations claimed. No TR_Setup advancement or playable level claimed.'
finish('scene-kill',scope,extra=extra)
shared_report={hex(a):{'total':len(code),'covered_on_kill':sum(bool(shared_hits[i.address]) for i in code),
 'unexecuted':[hex(i.address) for i in code if not shared_hits[i.address]]} for a,code in shared.items()}
(folder/'scene-kill-shared-coverage.json').write_text(json.dumps({'scope':'Only constant operation1; other operation branches intentionally excluded, not counted as recovered functions','helpers':shared_report},indent=2)+'\n')
