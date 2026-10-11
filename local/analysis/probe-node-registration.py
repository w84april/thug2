"""Full original node-array registration, iteration and link-group rebuilding."""
from pathlib import Path
source=Path('local/analysis/probe-node-index.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved index graph setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
global_default('thug_node_link_groups_draft',0x6f2264,0)
specs=[(0x45d050,187,'thug_node_iteration_start_draft',1,'void',False,True),
 (0x45d3f0,113,'thug_node_iteration_next_draft',0,'word',False,True),
 (0x45d110,10,'thug_node_iteration_end_draft',0,'void',False,True),
 (0x45c1d0,17,'thug_node_iteration_start_global_draft',1,'void',False,False),
 (0x45c1f0,11,'thug_node_iteration_next_global_draft',0,'word',False,False),
 (0x45c200,11,'thug_node_iteration_end_global_draft',0,'void',False,False),
 (0x45c020,44,'thug_node_link_count_draft',1,'word',False,False),
 (0x45c420,60,'thug_node_link_target_draft',2,'word',False,False),
 (0x4694e0,85,'thug_node_link_groups_get_draft',0,'word',True,False),
 (0x469540,62,'thug_node_reference_list_clear_draft',0,'void',False,True),
 (0x4696c0,341,'thug_node_link_groups_rebuild_draft',0,'void',True,True),
 (0x45d520,336,'thug_node_register_array_draft',2,'byte',True,True)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,name,argc,result,heap,this=this)
bind(0x45d370,'thug_node_table_initialize_draft',0,'word')
GROUP=0x9c91c3ca;CLASS=0x12b4e660;LINKS=0x2e7d5ee7;NAME=0xa1dc81f9;WAYPOINT=0x4c23a77e
class RegistrationGraph(IndexGraph):
    def __init__(self):
        super().__init__();self.image[NODETABLE+0x10000-BASE:NODETABLE+0x100fc-BASE]=bytes(0xfc)
        self.put(NODETABLE+0x10002,'<H',65535)
        self.position_nodes=[]
    def nodes_from(self,specs,raw_links=False):
        names=[s.get('name',0x11223fff+i*0x4000) for i,s in enumerate(specs)];nodes=[]
        for i,s in enumerate(specs):
            items=[(NAME,13,names[i])]
            if 'class' in s:items.append((CLASS,13,s['class']))
            if 'type' in s:items.append((0x7321a8d6,13,s['type']))
            if 'links' in s:items.append((LINKS,12,self.array(1 if raw_links else 13,[j if raw_links else names[j] for j in s['links']])))
            if 'group' in s:items.append((GROUP,1,s['group']))
            if s.get('group_flag'):items.append((0,13,GROUP))
            if 'position' in s:
                v=self.alloc(16);self.put(v,'<4I',0,*s['position']);items.append((0xb9d31b0a,6,v))
            if 'pos' in s:
                v=self.alloc(16);self.put(v,'<4I',0,*s['pos']);items.append((0x7f261953,6,v))
            items+=s.get('extra',[]);nodes.append(self.structure(items))
            if 'position' in s:self.position_nodes.append(nodes[-1])
            if 'text' in s:self.local_name(names[i],s['text'])
        return self.array(10,nodes),nodes,names
    def bind_arrays(self,arrays):
        self.put(NODETABLE+0x10004,'<I',len(arrays))
        for ai,(array,nodes,names) in enumerate(arrays):
            self.put(NODETABLE+0x10008+ai*12,'<3I',0x70000000+ai,array,0xa5a5a501)
            for ni,name in enumerate(names):
                slot=name&0x3fff
                while self.word(NODETABLE+slot*4)>>16!=65535:slot=(slot+1)&0x3fff
                self.put(NODETABLE+slot*4,'<HH',ai,ni)
    def refs(self,count,pattern='all'):
        p=self.alloc(8);refs=self.alloc(max(count,1)*12);objects=[self.alloc(8),self.alloc(8)]
        for o in objects:self.put(o,'<2I',0x12345678,0)
        for i in range(max(count,1)):self.put(refs+i*12,'<3I',0,0xabc00000+i,0xdef00000+i)
        for i in range(max(count,0)):
            if pattern=='null' or (pattern=='mixed' and i%2):continue
            o=objects[i%2];head=self.word(o+4);at=refs+i*12
            self.put(at,'<3I',o,0,head)
            if head:self.put(head+4,'<I',at)
            self.put(o+4,'<I',at)
        self.put(p,'<2I',refs,count&0xffffffff);return p
    def groups(self,counts=(0,)):
        manager=self.alloc(16);lists=self.alloc(max(len(counts),1)*8)
        for i,n in enumerate(counts):
            one=self.refs(n,'mixed');self.put(lists+i*8,'<2I',self.word(one),n&0xffffffff)
        self.put(manager,'<4I',lists,0x12345678,0x76543210,len(counts));return manager

# Preserve raw emulator output. The existing checker requires the exact Intel
# quiet bit (not NaN classification) only in the Y/Z coordinates loaded by x87.
# X is a MOV and remains an exact signaling payload. Registration never frees
# these newly converted vectors; subsequent duplicate calls preserve them.
quiet_differences=[]
def check(g,calls,label,changes=None):
    stages=case(calls,g.patches(),changes,label)
    if any(c[0]==0x45d520 for c in calls):
        typed=[]
        for node in g.position_nodes:
            component=oracle.word(node+4)
            while component and oracle.word(component+4)!=0x7f261953:component=oracle.word(component+12)
            assert component
            vector=oracle.word(component+8)
            for at in [vector+8,vector+12]:
                raw=oracle.word(at)
                if raw&0x7f800000==0x7f800000 and raw&0x7fffff and not raw&0x400000:
                    typed.append(at);quiet_differences.append({'case':len(labels)-1,'address':at,'oracle_word':raw,'intel_quiet_word':raw|0x400000})
        for stage in stages:stage['quiet_float_fields']=typed
    return stages

for sizes in [(1,),(3,),(2,1,3)]:
 for global_ in [False,True]:
  for start_at in [0,1,-1]:
    g=RegistrationGraph();arrays=[]
    for ai,n in enumerate(sizes):arrays.append(g.nodes_from([{'name':0x20003fff+0x4000*(j+ai*10)} for j in range(n)]))
    g.bind_arrays(arrays);flat=[n for a in arrays for n in a[1]];names=[n for a in arrays for n in a[2]]
    first=0 if start_at==0 else len(flat)-1 if start_at<0 else min(1,len(flat)-1)
    name=0 if start_at==0 else names[first]
    begin=call(0x45c1d0,args=[name]) if global_ else call(0x45d050,NODETABLE,[name])
    next_=call(0x45c1f0) if global_ else call(0x45d3f0,NODETABLE)
    end=call(0x45c200) if global_ else call(0x45d110,NODETABLE)
    stages=check(g,[begin]+[next_]*(len(flat)-first+2)+[end,next_],f'iterate{sizes},global{global_},start{start_at}')
    assert [s['result'] for s in stages[1:1+len(flat)-first]]==flat[first:]
    assert all(s['result']==0 for s in stages[1+len(flat)-first:-2])
for current,count in [(0,0),(0,0xffffffff),(0,0x80000000),(32767,32768),(32768,32769),(65534,0x7fffffff)]:
    g=RegistrationGraph();node=g.structure([]);array=g.array(10,[]);storage=BASE+0x300000
    signed=current if current<32768 else current-65536
    g.put(array+4,'<2I',count,storage);g.put(storage+signed*4,'<I',node)
    g.put(NODETABLE+0x10000,'<HHI',0,current,1);g.put(NODETABLE+0x1000c,'<I',array)
    s=check(g,[call(0x45d3f0,NODETABLE)],f'iteration signed node{current}/count{count:x}');assert s[0]['result']==node
for raw in [0,0x10001,0x7fff8000,0xffffffff]:
    g=RegistrationGraph();g.put(NODETABLE+0x10000,'<I',raw)
    check(g,[call(0x45d110,NODETABLE),call(0x45c200),call(0x45c1f0)],f'end preserves array half{raw:x}')
for shape in ['missing','wrong type','null','empty','one','three','included']:
    g=RegistrationGraph();array=g.array(13,[1,2,3] if shape=='three' else [1] if shape=='one' else [])
    items=[] if shape=='missing' else [(LINKS,1 if shape=='wrong type' else 12,0 if shape=='null' else array)]
    node=g.structure(items)
    if shape=='included':g.symbol(0x78900001,10,node);node=g.structure([(0,13,0x78900001)])
    check(g,[call(0x45c020,args=[node])],'link count '+shape)
for missing in [False,True]:
    g=RegistrationGraph();array,nodes,names=g.nodes_from([{'links':[2,0,1]},{},{}]);g.bind_arrays([(array,nodes,names)])
    if missing:g.put(NODETABLE+(names[2]&0x3fff)*4,'<HH',0,65535)
    check(g,[call(0x45c420,args=[nodes[0],i]) for i in range(3)],'link lookup missing'+str(missing))
for existing in [0,1]:
    g=RegistrationGraph();manager=g.groups((1,2))
    s=check(g,[call(0x4694e0)]*2,'manager getter existing'+str(existing),{0x6f2264:manager if existing else 0})
    assert s[0]['result']==s[1]['result']
for n,pattern in itertools.product([-1,0,1,2,5],['all','mixed','null']):
    g=RegistrationGraph();p=g.refs(n,pattern)
    check(g,[call(0x469540,p)]*2,f'clear refs{n}/{pattern}')
# An actual unlink can change the aliased live count to zero after one reference.
g=RegistrationGraph();p=g.alloc(8);ref=g.alloc(12);g.put(p,'<2I',ref,ref);g.put(ref,'<3I',p,0,0)
check(g,[call(0x469540,p)],'reference target head aliases live list count')
g=RegistrationGraph();p=g.alloc(16);g.put(p,'<4I',0,0xffffffff,0x12345678,0x7fffffff)
check(g,[call(0x4696c0,p)],'null list manager preserves all state')
patterns=[
 [{'class':0}],
 [{'class':WAYPOINT}],
 [{'class':WAYPOINT,'type':0xcba10ffa}],
 [{'class':WAYPOINT,'type':123}],
 [{'class':0x8e6b02ad,'links':[0]},{'class':0x30c19600,'links':[1]}],
 [{'links':[1]},{}],
 [{'links':[1]},{'links':[2]},{}],
 [{'links':[0]}],
 [{'links':[1]},{'links':[0]}],
 [{'links':[1,2]},{},{'class':WAYPOINT}],
 [{'links':[1]},{'links':[0]},{'links':[0]},{'class':WAYPOINT}],
 [{'links':[1]},{'group':19}],
 [{'links':[1]},{'group':0}],
 [{'links':[1]},{'group':0xffffffff}],
 [{'class':WAYPOINT,'group_flag':True}],
 [{'class':WAYPOINT,'group':77}],
 [{'class':WAYPOINT,'extra':[(GROUP,13,123)]}],
]
for i,spec in enumerate(patterns):
 for counts in [(),(0,),(-1,2,3)]:
    g=RegistrationGraph();a=g.nodes_from(spec);g.bind_arrays([a]);manager=g.groups(counts)
    check(g,[call(0x4696c0,manager)]*2,f'group graph{i}/refs{counts}')
# Null node ends outer iteration immediately; no fabricated scene callbacks.
g=RegistrationGraph();array=g.array(10,[0]);g.put(NODETABLE+0x10004,'<3I',1,1,array);manager=g.groups(())
check(g,[call(0x4696c0,manager)],'null first node ends traversal')

positions=[(0,0,0),(0x80000000,0x80000000,0x80000000),(0x3f800000,0xc0000000,0x40400000),
 (0x7f800000,0xff800000,1),(0x7fa12345,0xffa23456,0x7fa34567),(0xffc12345,0x7fc23456,0xffc34567)]
for flag in [0,1,2,255,256,257,0xffffffff]:
 for mode in ['empty','plain','coordinates','links','groups','existing groups']:
    g=RegistrationGraph();spec=[] if mode=='empty' else [{'name':0x99000001,'text':'test_01'}]
    if mode=='coordinates':spec=[{'position':p,'pos':(0x11111111,0x22222222,0x33333333),'text':f'point_{i:02}'} for i,p in enumerate(positions)]
    if mode in ['links','groups','existing groups']:spec=[{'links':[1],'position':positions[2],'text':'first_01'},{'class':WAYPOINT,'text':'last_02'}]
    a,nodes,names=g.nodes_from(spec,True);name=0x55001234;g.symbol(name,12,a)
    manager=g.groups((-1,2)) if mode in ['groups','existing groups'] else 0
    if mode=='existing groups':spec_group=g.alloc(16);g.put(spec_group,'<4I',0,0xaabbccdd,77,9);manager=spec_group
    # Registration with an empty array uses the original lazy manager's null-list
    # early return. Populated group lists require nonempty valid iteration state.
    stages=check(g,[call(0x45d520,NODETABLE,[name,flag])]*2,f'register{mode}/flag{flag:x}',{0x6f2264:manager,0x6f0d80:0})
    assert [s['result'] for s in stages]==[1,0]
# Multiple arrays, alias resolution and duplicate registration by stored name.
g=RegistrationGraph();calls=[]
for ai in range(3):
    a,_,_=g.nodes_from([{'name':0x88770000+ai,'class':WAYPOINT,'text':f'multi_{ai:02}'}],True)
    key=0x65000001+ai;g.symbol(key,12,a);calls.append(call(0x45d520,NODETABLE,[key,1]))
g.symbol(0x65000004,13,0x65000003);calls.append(call(0x45d520,NODETABLE,[0x65000004,256]))
manager=g.groups((1,));check(g,calls+[calls[1]],'multiple registered arrays and alias',{0x6f2264:manager})

excluded={'0x4694f2':'initialized allocator skips process bootstrap',
 '0x46952d':'test heap guarantees successful16-byte manager allocation',
 '0x46952f':'test heap guarantees successful16-byte manager allocation',
 '0x46979d':'unreachable alignment after unconditional jump'}
scope='Twelve complete original entry points recover full node-array registration, table/global iteration, link counts/targets, lazy link-group manager, reference-list cleanup and link-group rebuilding. Registration constructs actual name/prefix indexes, converts coordinates, resolves links and conditionally runs real group processing using the low flag byte. Cases cover duplicate registration, aliases/multiple arrays, cycles, chains merging into prior group IDs, excluded classes/PedAI, flag fields, reference unlinking and a live aliased count, signed iteration and halfword wrap. All callees execute; no scene/gameplay callbacks or registration success stubs are supplied. Full arena/globals/heap and preserved original registers compare. Signaling-NaN Y/Z fields require the exact Intel x87 quiet bit with sign/payload retained; raw emulator differences are recorded and X remains exact. No NaN classification allowances. Initialized allocator, successful allocations, valid linked targets and bounded table/array storage are internal contracts. This does not create/render the scene or complete TR_Setup.'
finish('node-registration',scope,excluded,{'pointer_result_exports':[], 'pointer_exports':exports})
(folder/'node-registration-x87-differences.json').write_text(json.dumps({'affected_fields':quiet_differences,'reason':'Unicorn can retain signaling payloads across original FLD/FSTP; require the exact Intel quiet bit in typed Y/Z only. Raw original fixtures are retained.'},indent=2)+'\n')
(folder/'node-registration-function-instructions.txt').write_text('\n'.join('\n'.join([hex(a)+' '+functions[hex(a)]['name']]+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in coverage[a]]) for a in coverage)+'\n')
