"""Original node hash/prefix construction and link conversion, with real callees."""
from pathlib import Path
source=Path('local/analysis/probe-scene-kill.py').read_text().split('for count,value in itertools.product')[0]
exec(compile(source,'<preserved graph and registry oracle setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
old_size=SIZE;SIZE=0x600000;oracle.cpu.mem_map(BASE+old_size,SIZE-old_size)
memory=bytearray(initial);memory.extend(bytes(SIZE-old_size))
LOCALNAMES,DEBUG,DSTRINGS=BASE+0xb0000,BASE+0x100000,BASE+0xe0000
memory[LOCALNAMES-BASE:LOCALNAMES-BASE+49152]=bytes(49152)
put(CONTEXT+20,'<I',BASE+SIZE);initial=bytes(memory);oracle.initial=initial
def global_default(name,at,value):
    if at in index:defaults[index[at]]=value
    else:glob(name,at,value)
for n,a,v in [('thug_script_local_names',0x6f2368,LOCALNAMES),('thug_script_debug_names',0x6f232c,DEBUG),
 ('thug_script_debug_cursor',0x6f2334,DSTRINGS)]:global_default(n,a,v)
if 0x7cefac in index:defaults[index[0x7cefac]]=0
else:glob('thug_script_debug_enabled',0x7cefac,0,1)
specs=[(0x45d370,45,'thug_node_table_initialize_draft',0,'word',False,True),
 (0x45ce60,144,'thug_node_table_insert_draft',3,'void',False,True),
 (0x45d3a0,65,'thug_node_table_index_array_draft',1,'void',False,True),
 (0x46f9b0,50,'thug_script_local_name_draft',1,'word',False,False),
 (0x45bda0,99,'thug_node_prefix_append_draft',1,'void',True,True),
 (0x45c650,161,'thug_node_prefix_add_draft',2,'void',True,True),
 (0x45c240,138,'thug_node_prefix_compact_draft',0,'void',True,True),
 (0x45c5d0,119,'thug_node_prefix_array_initialize_draft',0,'word',True,True),
 (0x45c700,512,'thug_node_prefix_build_draft',1,'void',True,True),
 (0x45c900,79,'thug_node_prefix_build_global_draft',1,'void',True,False),
 (0x46caf0,10,'thug_script_array_set_type_draft',1,'void',False,True),
 (0x45d480,151,'thug_node_links_resolve_draft',1,'void',False,False)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,name,argc,result,heap,this=this)
functions['0x45d480']['cleanup']=4 # stack argument, callee-cleaned original ABI
bind(0x45bf90,'thug_node_prefix_find_global_draft',2,'word',this=False)
functions['0x45bf90']['pointer_result']=True
exports.append([0x6efde0,'thug_node_prefix_results_draft'])
bind(0x45c1b0,'thug_node_find',2,'word',this=False)
COUNT=BASE+0x91c00
class IndexGraph(Graph):
    def alloc(self,n):
        p=super().alloc(n);assert self.cursor<LOCALNAMES;return p
    def text(self,s):
        raw=s.encode('latin1')+b'\0';p=self.alloc(len(raw));self.image[p-BASE:p-BASE+len(raw)]=raw;return p
    def local_name(self,name,text,head_null=False):
        bucket=LOCALNAMES+(name&4095)*12;value=0 if text is None else self.text(text)
        if self.word(bucket+4) or head_null:
            p=self.alloc(12);self.put(p,'<3I',name,value,self.word(bucket+8));self.put(bucket+8,'<I',p)
            if head_null:self.put(bucket,'<2I',name,0)
        else:self.put(bucket,'<3I',name,value,0)
        return value
    def array_symbol(self,texts):
        nodes=[]
        for i,text in enumerate(texts):
            name=crc(text) if text is not None else 0x20000000+i
            if text is not None:self.local_name(name,text)
            nodes.append(self.structure([(0xa1dc81f9,13,name)]))
        a=self.array(10,nodes);name=0x70000000+(self.cursor&0xffff);self.symbol(name,12,a)
        return name,a,nodes
def check(g,calls,label,changes=None):return case(calls,g.patches(),changes,label)

for fill in [0,0xa5,0xff]:
    g=IndexGraph();g.image[NODETABLE-BASE:NODETABLE-BASE+0x100fc]=bytes([fill])*0x100fc
    s=check(g,[call(0x45d370,NODETABLE)]*2,'constructor fill '+str(fill));assert all(x['result']==NODETABLE for x in s)
for key,kind,ai,ni in [(0,0,0,0),(0x3fff,0,1,2),(0xffffffff,0,0xffff,0xffff),(0x7fff,0,0x10001,0x18000),(1,0xc953660e,3,4),(2,None,3,4)]:
    g=IndexGraph();node=g.structure([(0xa1dc81f9,13,key)]+([(0x12b4e660,13,kind)] if kind is not None else []))
    calls=[call(0x45ce60,NODETABLE,[ai,ni,node])]*3
    check(g,calls,f'insert name{key:x},kind{kind},indices{ai}/{ni}')
g=IndexGraph();check(g,[call(0x45ce60,NODETABLE,[0,3,g.structure([])])],'missing Name')
for ai,n in itertools.product([0,19],[0,1,4]):
    g=IndexGraph();nodes=[g.structure([(0xa1dc81f9,13,0x3fff+i*0x4000),(0x12b4e660,13,0xc953660e if i==2 else 0)]) for i in range(n)]
    array=g.array(10,nodes);g.put(NODETABLE+0x1000c+ai*12,'<I',array)
    check(g,[call(0x45d3a0,NODETABLE,[ai])]*2,f'index array{ai},count{n}')
# The name getter traverses included structures, as in actual TR.qb.
g=IndexGraph();included=g.structure([(0xa1dc81f9,13,0x3fff)]);g.symbol(0x77000001,10,included)
node=g.structure([(0,13,0x77000001)]);check(g,[call(0x45ce60,NODETABLE,[7,8,node])],'included Name')
for mode in ['absent table','empty','head','collision','missing','null head equal']:
    g=IndexGraph();key=0x55667788
    g.local_name(key^0x1000,'other');text=g.local_name(key,'target',mode=='null head equal')
    if mode=='head':g.put(LOCALNAMES+(key&4095)*12,'<3I',key,text,0)
    if mode=='empty':g.put(LOCALNAMES+(key&4095)*12,'<3I',0,0,0)
    stages=check(g,[call(0x46f9b0,args=[key^0x2000 if mode=='missing' else key])],mode,{0x6f2368:0} if mode=='absent table' else None)
    assert stages[0]['result']==(0 if mode in ['absent table','empty','missing','null head equal'] else text)
for count,value in itertools.product([-1,0,98,99,100,199],[0,0x10001,0xffffffff]):
    g=IndexGraph();p=g.alloc(12);items=g.alloc(500)+2
    for i in range(-1,220):g.put(items+i*2,'<H',(i+17)&0xffff)
    g.put(p,'<3I',count&0xffffffff,items,0x12345678)
    check(g,[call(0x45bda0,p,[value])],f'append count{count}/value{value:x}')
for shape in ['empty','head','collision','null head','missing collision']:
    g=IndexGraph();entry=g.alloc(12);lists=[]
    for i in range(2):
        p=g.alloc(12);items=g.alloc(220);g.put(p,'<3I',0,items,3+i*4);lists.append(p)
    t=g.table([] if shape=='empty' else [(3,lists[0])])
    if shape in ['collision','null head','missing collision']:
        tail=g.alloc(12);g.put(tail,'<3I',7 if shape!='missing collision' else 11,lists[1],0)
        g.put(g.word(t+4)+3*12+8,'<I',tail)
        if shape=='null head':g.put(g.word(t+4)+3*12+4,'<I',0)
    g.put(entry,'<3I',t,0x9876,0)
    check(g,[call(0x45c650,entry,[7,0x12345]),call(0x45c650,entry,[7,0x54321])],shape)
for counts in [[],[0],[1],[3,0,2],[2,None,3]]:
    g=IndexGraph();entry=g.alloc(12);values=[]
    for n in counts:
        if n is None:values.append(0);continue
        p=g.alloc(12);items=g.alloc(max(2*n,2));g.put(p,'<3I',n,items,7)
        for i in range(n):g.put(items+i*2,'<H',0x4321+i)
        values.append(p)
    table=g.table([]);bucket=g.word(table+4)
    if values:
        g.put(bucket,'<3I',0,values[0],0);tail=bucket
        for v in values[1:]:
            q=g.alloc(12);g.put(q,'<3I',0,v,0);g.put(tail+8,'<I',q);tail=q
    g.put(entry,'<3I',table,7,0)
    check(g,[call(0x45c240,entry)]*2,'compact '+str(counts))
g=IndexGraph();entry=g.alloc(12);check(g,[call(0x45c5d0,entry)],'prefix entry constructor')

groups=[[],[None],[''],['abc'],['123'],['foo1','foo2'],['foo_01','foo_02','foo__03'],
 ['TRG_A1','trg_01','TrG_zone_001','TRG'],['_','_12','a_','a9z','\xff_2'],
 ['x'*997+'01'],['a__b_12c_003'],['same_%03d'%i for i in range(201)]]
for number,texts in enumerate(groups):
 for debug in [0,1]:
    g=IndexGraph();name,array,nodes=g.array_symbol(texts)
    check(g,[call(0x45c900,args=[name])],f'prefix group{number},debug{debug}',{0x7cefac:debug,0x6f0d80:0})
# Existing nonempty manager and aliases, then actual prefix lookup preserves
# array order (new arrays prepend); repeated node indices remain meaningful.
g=IndexGraph();name1,a1,_=g.array_symbol(['test_02','test_01']);name2,a2,_=g.array_symbol(['test_03'])
g.symbol(0x77112233,13,name2)
check(g,[call(0x45c900,args=[name1]),call(0x45c700,PREFIX,[0x77112233]),call(0x45c900,args=[name1]),call(0x45bf90,args=[crc('test_'),COUNT])],
 'multiple arrays, alias and real prefix lookup',{0x7cefac:1})
assert int.from_bytes(oracle.cpu.mem_read(COUNT,2),'little')==5
g=IndexGraph();name,_,_=g.array_symbol(['x_1']);check(g,[call(0x45c700,PREFIX,[name])],'missing local names still constructs empty index',{0x6f2368:0})
for value in [0,1,13,127,128,255,256,257,0xffffffff]:
    g=IndexGraph();a=g.array(0x91,[0x12345678]);check(g,[call(0x46caf0,a,[value])],f'type low byte{value:x}')
for shape in ['empty','no links','empty links','single','multiple','missing name']:
    g=IndexGraph();nodes=[]
    count=0 if shape=='empty' else 1 if shape=='single' else 3
    for i in range(count):
        links=g.array(1,[] if shape=='empty links' else [0] if shape=='single' else [2,0,1])
        items=[] if shape=='missing name' and i==1 else [(0xa1dc81f9,13,0x11220000+i)]
        if shape not in ['no links','empty']:items.append((0x2e7d5ee7,12,links))
        nodes.append(g.structure(items))
    a=g.array(10,nodes);check(g,[call(0x45d480,args=[a])],'links '+shape)

excluded={'0x45c28d':'unreachable alignment padding after an unconditional jump',
 '0x45c5f2':'initialized allocator skips process bootstrap',
 '0x45c623':'failed table allocation outside successful live-object contract',
 '0x45c6cd':'failed list allocation cannot provide required live storage',
 '0x45c762':'failed entry allocation cannot provide required live storage',
 '0x45c931':'failed manager allocation cannot provide required live storage'}
scope='Twelve original routines recover node hash-table construction/insertion/array indexing, local readable-name lookup, prefix-list growth/addition/compaction, prefix-array construction and full manager/global prefix building, array type setting and node-link conversion. Actual lookup, allocation, local/global symbols, debug names and prefix result lookup run. Cases cover duplicate and wrapping hash slots, included Names, low-half indices, first-null local names, hundred-entry growth, zero lists, TRG suppression, underscore/digit prefixes, retained multi-array order and links converted to node checksums. C-locale text, initialized allocator, successful allocations and bounded names/indexes are internal contracts. Full arena/globals/heap effects and preserved original registers compare. Complete node-array registration and its optional postprocessing remain; no playable level.'
finish('node-index',scope,excluded,{'pointer_result_exports':[], 'pointer_exports':exports})
