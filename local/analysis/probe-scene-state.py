"""Six original scene state routines with full-arena differential fixtures."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph/oracle helpers>','exec'))
functions.clear()
specs=[(0x48c7f0,20,'thug_scene_first_draft',False,'word',0),
       (0x44e4e0,11,'thug_network_scene_mode_draft',True,'word',0),
       (0x57d7c0,125,'thug_rail_set_enabled_draft',True,'void',12),
       (0x468340,109,'thug_emitter_set_enabled_draft',False,'void',0),
       (0x48de60,5,'thug_render_set_enabled_draft',True,'void',4),
       (0x49e9b0,44,'thug_geometry_set_enabled_draft',True,'void',4)]
coverage={};hits=Counter();saved_by=[]
for a,n,name,this,result,cleanup in specs:
    functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':cleanup}
    code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a));coverage[a]=code
    oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
scene_i=len(globals_);globals_.append(['thug_collision_scene_list',0x6fa7ec,4]);defaults.append(0)
emitter_i=len(globals_);globals_.append(['thug_emitter_table_draft',0x6f2260,4]);defaults.append(0)
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x588190,end=0x588190)
VT=BASE+0x5200;CB=oracle.stop+0x200;CBLOG=BASE+0x5000;CBCONTROL=BASE+0x5100
def callback(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);render=cpu.reg_read(UC_X86_REG_ECX);enabled=oracle.word(sp+4)
    watch=oracle.word(CBCONTROL);write=oracle.word(CBCONTROL+4)
    oracle.setword(CBLOG,oracle.word(CBLOG)+1);oracle.setword(CBLOG+4,render);oracle.setword(CBLOG+8,enabled)
    oracle.setword(CBLOG+12,oracle.word(watch) if watch else 0x13579bdf)
    if write:oracle.setword(write,oracle.word(CBCONTROL+8))
    cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+8)
oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=CB,end=CB)
labels=[]
def run(g,calls,label,changes=None):
    g.put(VT+0x34,'<I',CB);g.put(CBLOG,'<4I',0,0,0,0)
    if g.word(CBCONTROL)==0xadadadad:g.put(CBCONTROL,'<3I',0,0,0)
    before=[oracle.cpu.reg_read(r) for r in registers]
    stages=oracle.case(calls,g.patches(),changes)
    assert [oracle.cpu.reg_read(r) for r in registers]==before,label
    previous=0
    for s in stages:
        for at,data in s['outputs']:
            if at==CBLOG:
                now=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=now-previous;previous=now
    labels.append(label);return stages

for scene in [0,0xffffffff,0x12345678]:
    g=Graph();head=g.alloc(16);g.put(head,'<4I',0x11223344,scene,0xabcdef,0xfefefefe)
    s=run(g,[(0x48c7f0,0,[])],'scene sentinel '+hex(scene),{scene_i:head})
    assert s[0]['result']==(0 if scene==0xffffffff else head)
for value in [*range(256),0x80000000,0xffffffff,0x7ffffff3,0xa5a5a508]:
    g=Graph();state=g.alloc(4);g.put(state,'<I',value)
    s=run(g,[(0x44e4e0,state,[])],'network flags '+hex(value));assert s[0]['result']==int(bool(value&12))
for count in [-3,0,1,4,7]:
 for index in [-1,0,3,6]:
  for enabled,recursive in itertools.product([0,1,256,0xffffffff],[0,1,256,0x101]):
    g=Graph();manager=g.alloc(0x50);nodes=g.alloc(7*0x54);external=g.alloc(0x54)
    for i in range(7):
        g.put(nodes+i*0x54+0x40,'<4I',external if i==index else 0,0,0xa5a5a5a1|(4 if i&1 else 0),0x1234 if i==index else 0x5678)
    g.put(external+0x40,'<4I',0,0,0xfffffff0,0x7654)
    g.put(manager+0x40,'<3I',nodes,0xabcdef01,count&0xffffffff)
    run(g,[(0x57d7c0,manager,[0x1234,enabled,recursive])]*2,f'rail count{count},index{index},enabled{enabled:x},recursive{recursive:x}')
# Duplicate names: only the first match is changed. Linked traversal follows
# pointers, including reordered array entries, rather than consecutive storage.
for recursive in [0,1]:
    g=Graph();manager=g.alloc(0x50);nodes=g.alloc(4*0x54)
    for i in range(4):g.put(nodes+i*0x54+0x40,'<4I',nodes+3*0x54 if i==0 else nodes+2*0x54 if i==3 else 0,0,0xffffffff,0x1234)
    g.put(manager+0x40,'<3I',nodes,0,4)
    run(g,[(0x57d7c0,manager,[0x1234,0,recursive])],'rail first duplicate/linked reorder '+str(recursive))

def emitter_table(g,heads,chains,shift=2):
    table=g.alloc(24);buckets=g.alloc((1<<(shift&31))*12)
    g.put(table,'<6I',shift,buckets,93,0xabcdef01,0xfefefefe,0x11223344)
    for i in range(1<<(shift&31)):
        tail=0
        for value in reversed(chains.get(i,[])):
            node=g.alloc(12);g.put(node,'<3I',i,value,tail);tail=node
        g.put(buckets+i*12,'<3I',i,heads.get(i,0),tail)
    return table
for shape in ['empty','inline first','inline last','collision','null head collision','null collision stops','null first collision','duplicate','missing']:
 for enabled in [0,1,255,256,0xffffffff]:
    g=Graph();items=[g.alloc(0x28) for _ in range(4)]
    for i,p in enumerate(items):g.put(p,'<I',0x1234 if i in [1,3] else 0x4567)
    heads={};chains={}
    if shape=='inline first':heads={0:items[1]}
    elif shape=='inline last':heads={0:items[0],3:items[1]}
    elif shape=='collision':heads={0:items[0]};chains={0:[items[2],items[1]]}
    elif shape=='null head collision':chains={0:[items[1]]}
    elif shape=='null collision stops':heads={0:items[0],3:items[1]};chains={0:[0,items[1]]}
    elif shape=='null first collision':chains={0:[0,items[1]]}
    elif shape=='duplicate':heads={0:items[1],3:items[3]}
    elif shape=='missing':heads={0:items[0],3:items[2]}
    table=emitter_table(g,heads,chains)
    run(g,[(0x468340,0,[0x1234,enabled])]*2,f'emitter {shape}/{enabled:x}',{emitter_i:table})

for enabled in [0,1,2,255,256,257,0x80000000,0xffffffff]:
 for collision_flags in [0,4,0x80,0xff,0xfe]:
  for have_collision,have_render in [(0,0),(0,1),(1,0),(1,1)]:
    g=Graph();geometry=g.alloc(0x20);collision=g.alloc(0x10);render=g.alloc(8)
    g.put(geometry+0x14,'<2I',render if have_render else 0,collision if have_collision else 0)
    g.put(collision+8,'<I',0x12345600|collision_flags);g.put(render,'<I',VT)
    g.put(CBCONTROL,'<3I',collision+8,0,0)
    run(g,[(0x49e9b0,geometry,[enabled])]*2,f'geometry flag{collision_flags:x}/enabled{enabled:x}/pointers{have_collision}{have_render}')
for enabled in [0,1,256,0xffffffff]:
    g=Graph();render=g.alloc(8);g.put(render,'<I',VT)
    run(g,[(0x48de60,render,[enabled])],'direct virtual enabled '+hex(enabled))
# Alias collision flag byte to the render pointer. The changed pointer must be
# re-read before dispatch (both adjacent method receivers are valid).
for enabled in [0,1]:
    g=Graph();geometry=g.alloc(0x20);render=(g.alloc(0x100)+0x40)&~0xff
    render+=0x80;g.put(render,'<2I',VT,VT)
    g.put(geometry+0x14,'<2I',render+4 if enabled else render,geometry+0xc)
    run(g,[(0x49e9b0,geometry,[enabled])],'collision aliases render pointer '+str(enabled))

coverage_report={}
for a,code in coverage.items():
    missing=[hex(i.address) for i in code if not hits[i.address]];assert not missing,(hex(a),missing)
    coverage_report[hex(a)]={'covered':len(code),'total':len(code),'missing':[]}
scope='Six complete original routines: scene sentinel lookup, network flags 2/3 predicate, first-match rail enabling with linked recursion, emitter enabling through the actual stateful table iterator, renderer virtual forwarding and collision-before-render enabled state. Exact low-byte versus full-word boolean rules, negative counts, duplicate names, null-valued collision termination, retained calls and collision/render-pointer alias ordering are checked. Renderer is a test-only argument/state witness, not a renderer implementation. Entire arena and globals are compared with no NaN allowances; original callee-saved registers preserved. No complete Kill command or playable level established.'
fixture={'base':BASE,'memory':'scene-state-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'renderer_dispatches',
 'native_callbacks':[{'module':'scene-state-callback.wasm','export':'fixture_scene_enabled','slots':[VT+0x34]}]}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-state-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage_report,'callee_calls':dict(oracle.coverage),'scope':scope}
(folder/'scene-state-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
