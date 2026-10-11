"""Original table clearing and both light collections, including live reloads."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph/oracle helpers>','exec'))
functions.clear();functions.update({
 '0x49fd30':{'name':'thug_object_table_clear_draft','this':True,'result':'void','cleanup':0,'memory':True},
 '0x48fca0':{'name':'thug_scene_remove_light_draft','this':False,'result':'void','cleanup':0,'memory':True}})
indices={}
for name,address,size,default in [('thug_lookup_node_pool',0x7d1808,4,0),('thug_scene_light_count_draft',0x6faef0,4,0),
 ('thug_scene_lights_draft',0x6faaf0,256*4,0),('thug_decal_light_count',0x6faef4,4,0),('thug_decal_lights',0x6faf80,150*36,0xadadadad)]:
 for off in range(0,size,4):indices[address+off]=len(globals_);globals_.append([name,address+off,4,off]);defaults.append(default)
coverage={};hits=Counter()
for at,size in [(0x49fd30,94),(0x48fca0,253)]:
    coverage[at]=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,size),at))
    oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=at,end=at+size-1)
for at in [0x5bc4a0,0x5ba400]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
def release_record(kind,a,b,c):
    record_before(kind,a,b,c)
    if kind==2 and oracle.word(CONTROL):
        count=oracle.word(CONTROL+4)+1;oracle.setword(CONTROL+4,count)
        if count==oracle.word(CONTROL):
            for off in [8,16]:
                at=oracle.word(CONTROL+off)
                if at:oracle.setword(at,oracle.word(CONTROL+off+4))
oracle.record=release_record
labels=[]
def run(g,calls,label,changes=None):
    before=[oracle.cpu.reg_read(r) for r in registers]
    s=oracle.case(calls,g.patches(),changes)
    assert before==[oracle.cpu.reg_read(r) for r in registers],label
    labels.append(label);return s
def table(g,shift=2,lengths=(0,1,3,0),null=False):
    t=g.alloc(24);buckets=0 if null else g.alloc((1<<(shift&31))*12);nodes=[]
    if buckets:
      for i in range(1<<(shift&31)):
        tail=0
        for j in range(lengths[i%len(lengths)]):
            n=g.alloc(12);g.put(n,'<3I',0x10000+i*16+j,0 if j&1 else 0xf00d1000+j,tail);tail=n;nodes.append(n)
        g.put(buckets+i*12,'<3I',0x23450000+i,0xdead0000+i if i&1 else 0,tail)
    g.put(t,'<6I',shift,buckets,93,0x12345678,0xfeed1234,0xaabbccdd);return t,nodes
def pool(g,nodes):
    p=g.alloc(0x5c);tail=g.alloc(12)
    g.put(p,'<6I',BASE,BASE+SIZE,0x11223344,0x55667788,len(nodes),tail);g.put(tail,'<3I',0,0xabcdef01,0xabcdef02);g.put(p+0x58,'<I',91)
    return p
for shift in [0,1,2,5,32,33,34]:
 for lengths in [(0,),(1,),(0,2,1,4)]:
  for pooled in [False,True]:
    g=Graph();t,nodes=table(g,shift,lengths);changes={}
    if pooled:changes[indices[0x7d1808]]=pool(g,nodes)
    run(g,[(0x49fd30,t,[])]*2,f'table clear shift{shift},lengths{lengths},pool{pooled}',changes)
for null in [False,True]:
    g=Graph();t,_=table(g,0,(0,),null)
    run(g,[(0x49fd30,t,[])],'null buckets preserves count '+str(null))
for action in ['clear freed next','replace table buckets','replace shift','replace count']:
    g=Graph();t,nodes=table(g,2,(3,0,1,0));head=g.word(t+4);first=g.word(head+8)
    target,value={'clear freed next':(first+8,0),'replace table buckets':(t+4,g.alloc(48)),
                  'replace shift':(t,0),'replace count':(t+8,0x87654321)}[action]
    g.put(CONTROL,'<6I',1,0,target,value,0,0)
    run(g,[(0x49fd30,t,[])],'release callback '+action)

def setup_lights(g,scene_names,decal_names,pooled=False):
    changes={indices[0x6faef0]:len(scene_names),indices[0x6faef4]:len(decal_names)};nodes=[];lights=[];tables=[]
    for i,name in enumerate(scene_names):
        light=g.alloc(0x40);g.put(light+0x28,'<I',name);changes[indices[0x6faaf0+i*4]]=light;lights.append(light)
    for i,name in enumerate(decal_names):
        t,chain=table(g,1,(0 if i&1 else 2,1));nodes+=chain;tables.append(t)
        # Include signaling NaNs in the opaque copied position/intensity fields.
        record=[0x7f812345,0xff812345,0x80000000,0x12340000+i,0x7fc00100+i,0xff800000,name,0x12345678,t]
        for j,value in enumerate(record):changes[indices[0x6faf80+i*36+j*4]]=value
    if pooled:changes[indices[0x7d1808]]=pool(g,nodes)
    return changes,lights,tables
KEY=0x12345678;OTHER=0x54321000
for n,m in itertools.product([0,1,3,7],[0,1,3,7]):
 for match in ['none','first','middle','last','all']:
  for pooled in [False,True]:
    def names(count):return [KEY if match=='all' or (match!='none' and i=={'first':0,'middle':count//2,'last':count-1}.get(match,-1)) else OTHER+i for i in range(count)]
    g=Graph();changes,lights,tables=setup_lights(g,names(n),names(m),pooled)
    run(g,[(0x48fca0,0,[KEY])]*3,f'lights {n}/{m},match{match},pool{pooled}',changes)
# Full capacities and the different tail rules of the two arrays.
for match in ['first','last']:
    g=Graph();changes,_,_=setup_lights(g,[KEY if i==(0 if match=='first' else 255) else OTHER+i for i in range(256)],
                                   [KEY if i==(0 if match=='first' else 149) else OTHER+i for i in range(150)])
    run(g,[(0x48fca0,0,[KEY])]*2,'full light capacities '+match,changes)
for n,m in [(-1,0),(0,-1),(-0x80000000,-0x80000000)]:
    g=Graph();run(g,[(0x48fca0,0,[KEY])],f'negative collection counts {n}/{m}',{indices[0x6faef0]:n&0xffffffff,indices[0x6faef4]:m&0xffffffff})
for action in ['scene count','scene tail pointer','decal count','decal tail name']:
    g=Graph();changes,lights,tables=setup_lights(g,[KEY,OTHER,OTHER+1] if action.startswith('scene') else [],[KEY,OTHER,OTHER+1])
    target,value={'scene count':(0x6faef0,2),'scene tail pointer':(0x6faaf0+8,lights[1] if lights else 0),
                  'decal count':(0x6faef4,2),'decal tail name':(0x6faf80+2*36+24,0x99aabbcc)}[action]
    g.put(CONTROL,'<6I',1,0,target,value,0,0)
    run(g,[(0x48fca0,0,[KEY])],'release changes live '+action,changes)

coverage_report={}
for a,code in coverage.items():
    missing=[hex(i.address) for i in code if not hits[i.address]]
    # A 32-bit x86 shift masks its count, so 1<<cl cannot be zero.
    assert not missing,(hex(a),missing)
    coverage_report[hex(a)]={'covered':len(code),'total':len(code),'missing':[]}
scope='Complete original49fd30 table clearing and48fca0 light removal. Null buckets preserve count; bucket heads clear after collision releases; bucket base/limit and next links are captured before callbacks; table iteration fields survive. Both heap and real fixed-pool release paths run. Each light collection removes only its first matching name and re-reads counts after destruction; pointer-array tail clears, decal-record tail remains. Full256/150 capacities, duplicates, signed-negative counts, repeated deletion, exact signaling-NaN payload copies and release-induced live count/tail/table mutations are checked. Entire1MiB arena and both complete global collections compare exactly. Allocation services are explicit test ports; no light renderer or complete scene command is implemented.'
pointer_exports=[[0x6faef0,'thug_scene_light_count_draft'],[0x6faef4,'thug_decal_light_count'],[0x6faaf0+8,'thug_scene_lights_draft',8],[0x6faf80+96,'thug_decal_lights',96]]
fixture={'base':BASE,'memory':'scene-disposal-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'scene-disposal-memory.wasm',
 'memory_exports':['fixture_scene_allocate','fixture_scene_release','fixture_scene_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'pointer_exports':pointer_exports,'pointer_fields':[CONTROL+8,CONTROL+16],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'scene-disposal-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':coverage_report,'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'scene-disposal-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
