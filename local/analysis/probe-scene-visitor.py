"""Reentrant original object-list traversal, including callback mutations."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph/oracle helpers>','exec'))
functions.clear();functions['0x461cc0']={'name':'thug_object_manager_visit_draft','this':True,'result':'void','cleanup':8,'pointer_args':[0]}
CB=oracle.stop+0x200;CONTINUE=CB+0x10;CLOG=BASE+0x5000
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x61cc0,302),0x461cc0));hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=0x461cc0,end=0x461ded)
def finish(cpu,sp):
    cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
def callback(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP)
    if at==CONTINUE:finish(cpu,sp);return
    o=oracle.word(sp+4);c=oracle.word(sp+8);manager=oracle.word(c);log=oracle.word(c+4);bit=oracle.word(c+8)
    n=oracle.word(log);assert n<128;oracle.setword(log,n+1)
    cpu.mem_write(log+4+n*24,struct.pack('<6I',o,oracle.word(o+0x14),oracle.word(o+0x1c),oracle.word(manager+0x18),oracle.word(manager+0x1c),c))
    fired=oracle.word(c+16);oracle.setword(c+16,fired+1)
    if fired:finish(cpu,sp);return
    mode=oracle.word(c+12);target=oracle.word(c+20);value=oracle.word(c+24)
    if mode==1:oracle.setword(target+0x1c,oracle.word(target+0x1c)|bit)
    elif mode==2:
        p=oracle.word(target+12);n=oracle.word(target+16)
        oracle.setword(n+12,p);oracle.setword(p+16,n);oracle.setword(target+12,target);oracle.setword(target+16,target)
        oracle.setword(manager+0x1c,oracle.word(manager+0x1c)|value)
    elif mode==3:oracle.setword(target+4,value)
    elif mode==4:
        first=oracle.word(manager+16);oracle.setword(target+12,first);oracle.setword(target+16,manager+4)
        oracle.setword(first+16,target);oracle.setword(manager+16,target)
        oracle.setword(manager+0x1c,oracle.word(manager+0x1c)|bit)
    elif mode==5:oracle.setword(manager+0x1c,oracle.word(manager+0x1c)|bit)
    elif mode==6:
        child=oracle.word(c+28);cpu.mem_write(sp-12,struct.pack('<3I',CONTINUE,CB,child))
        cpu.reg_write(UC_X86_REG_ESP,sp-12);cpu.reg_write(UC_X86_REG_ECX,manager);cpu.reg_write(UC_X86_REG_EIP,0x461cc0);return
    elif mode==7:oracle.setword(manager+0x18,value)
    finish(cpu,sp)
oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=CB,end=CONTINUE)
labels=[]
def graph(count,used=0,restart=0,raw_visited=0):
    g=Graph();manager=g.alloc(0x28);objects=[g.alloc(0x4c) for _ in range(count)];sentinel=manager+4;nodes=[o+0x28 for o in objects]
    g.put(sentinel,'<5I',0xcccccccc,0xffffffff,0,nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel)
    g.put(manager+0x18,'<2I',used,restart)
    for i,(o,n) in enumerate(zip(objects,nodes)):
        g.put(o+0x14,'<3I',0x12340000+i,0x44556677,raw_visited)
        g.put(n,'<5I',0xcccccccc,o,0,nodes[i+1] if i+1<count else sentinel,nodes[i-1] if i else sentinel)
    bit=1
    while used&bit:bit=(bit<<1)&0xffffffff
    c=g.alloc(32);g.put(c,'<8I',manager,CLOG,bit,0,0,0,0,0);g.put(CLOG,'<I',0)
    return g,manager,objects,nodes,c,bit
def run(g,manager,c,label,repeat=1):
    g.put(BASE+0x6000,'<I',CB)
    before=[oracle.cpu.reg_read(r) for r in registers]
    s=oracle.case([(0x461cc0,manager,[CB,c])]*repeat,g.patches())
    assert before==[oracle.cpu.reg_read(r) for r in registers],label
    previous=0
    for stage in s:
        for at,data in stage['outputs']:
            if at==CLOG:
                now=int.from_bytes(bytes.fromhex(data),'little');stage['callbacks']=now-previous;previous=now
    labels.append(label);return s
for count,used,visited in itertools.product([0,1,4,17],[0,1,3,0x7fffffff,0x80000000,0xffffffff],[0,0xffffffff,0x55555555]):
    g,m,objects,nodes,c,bit=graph(count,used,0xffffffff,visited)
    run(g,m,c,f'list{count},used{used:x},visited{visited:x}',2)
for null_at in [0,1,3]:
    g,m,objects,nodes,c,bit=graph(4,3,0xffffffff,0xffffffff);g.put(nodes[null_at]+4,'<I',0)
    run(g,m,c,'null object terminates at '+str(null_at))
for used in [0,1,7,0x7fffffff]:
 for mode in [1,2,3,4,5,6,7]:
  for flag in [0,1]:
    g,m,objects,nodes,c,bit=graph(4,used,0xa5a5a5a5,0xffff0000)
    spare=g.alloc(0x4c);g.put(spare+0x14,'<3I',0x87654321,0,0)
    g.put(spare+0x28,'<5I',0xcccccccc,spare,0,spare+0x28,spare+0x28)
    target,value={1:(objects[2],0),2:(nodes[0],bit if flag else 0),3:(nodes[1],spare if flag else 0),
                  4:(spare+0x28,0),5:(0,0),6:(0,0),7:(0,0 if flag else 0xffffffff)}[mode]
    child=g.alloc(32);nextbit=(bit<<1)&0xffffffff
    g.put(child,'<8I',m,CLOG,nextbit,5 if flag else 0,0,0,0,0)
    g.put(c+12,'<5I',mode,0,target,value,child)
    run(g,m,c,f'mutation{mode},flag{flag},used{used:x}')
missing=[hex(i.address) for i in code if not hits[i.address]];assert not missing,missing
scope='Complete461cc0 normal-return object-manager traversal. Every instruction executes, including selection of nested visitation bits, initial per-object clearing, cached successor node/object, restart loops, already-visited skipping and live active-bit cleanup. Empty/sentinel/null-value lists, all32 bits occupied, repeated calls, removal with/without restart, replacing next object, inserting a head, marking a later object visited and actual nested calls compare. Callbacks are explicit test witnesses of mutation/order rather than invented object destruction. Full arena/globals/logs and original preserved registers match; native Windows exception unwinding is outside the normal-return callback contract. This does not complete Kill or make a level playable.'
fixture={'base':BASE,'memory':'scene-visitor-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'object_visits','pointer_fields':[BASE+0x6000],
 'native_callbacks':[{'module':'scene-visitor-callback.wasm','export':'fixture_scene_visit','original':CB,'engine_imports':['thug_object_manager_visit_draft']}]}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-visitor-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':{'0x461cc0':{'covered':len(code),'total':len(code),'missing':[]}},'scope':scope}
(folder/'scene-visitor-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
