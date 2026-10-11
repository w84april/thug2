"""Original populated node-prefix traversal, including two-byte index behavior."""
from pathlib import Path
prefix=Path('local/analysis/probe-script-change.py').read_text().split('labels=[];KEY=')[0]
exec(compile(prefix,'<preserved graph and original oracle>','exec'))
functions.clear();functions.update({'0x45be90':{'name':'thug_node_prefix_find_draft','result':'word','pointer_result':True,'cleanup':8},
 '0x45bf90':{'name':'thug_node_prefix_find_global_draft','this':False,'result':'word','pointer_result':True,'cleanup':0}})
PREFIX_MANAGER=BASE+0x6800;RESULTS=0x6efde0
memory=bytearray(initial);struct.pack_into('<I',memory,PREFIX_MANAGER-BASE,0);initial=bytes(memory);oracle.initial=initial
manager_index=len(globals_);globals_.append(['thug_node_prefix_manager_draft',0x6f0d80,4]);defaults.append(PREFIX_MANAGER)
for i in range(1000):globals_.append(['thug_node_prefix_results_draft',RESULTS+4*i,4,4*i]);defaults.append(0x5a5a0000+i)
instructions={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x45be90,255),(0x45bf90,22)]};hits=Counter();saved={}
def prefix_trace(cpu,at,size,user):
    hits[at]+=1
    for a,insns in instructions.items():
        if at==a:saved[a]=[cpu.reg_read(r) for r in registers]
        if at in {i.address for i in insns if i.mnemonic=='ret'}:assert saved[a]==[cpu.reg_read(r) for r in registers]
for a,insns in instructions.items():oracle.cpu.hook_add(UC_HOOK_CODE,prefix_trace,begin=a,end=insns[-1].address)
for a in [0x479070,0x46cc30]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
class PrefixGraph(Graph):
    def alloc(self,n):
        at=self.cursor;self.cursor=(at+n+19)&~3;assert self.cursor<BASE+SIZE;return at
    def patches(self):return [[BASE+i,self.image[i:i+4].hex()] for i in range(0,SIZE,4) if self.image[i:i+4]!=initial[i:i+4]]
    def entry(self,key,indices,node_names,shift=4,shape='direct',alias=False):
        nodes=[self.structure([] if n is None else [(0xa1dc81f9,13,n),(0xa1dc81f9,13,n+1)] if isinstance(n,int) and n&0x10000000 else [(0xa1dc81f9,13,n)]) for n in node_names]
        array=self.array(10,nodes);array_name=0xaabb0000+(self.cursor&0xffff)
        self.symbol(array_name,12,array)
        if alias:self.symbol(array_name+1,13,array_name);array_name+=1
        count=len(indices);values=self.alloc(max(count*2,2));self.put(values,'<'+'H'*count,*indices)
        found=self.alloc(8);self.put(found,'<HHI',count,0x9876,values)
        bucket_count=1<<(shift&31);buckets=self.alloc(bucket_count*12)
        for i in range(bucket_count):self.put(buckets+i*12,'<3I',0,0,0)
        head=buckets+(key&(bucket_count-1))*12
        if shape in ['collision','null-value']:
            tail=self.alloc(12);self.put(tail,'<3I',key,found,0);self.put(head,'<3I',key if shape=='null-value' else key^1,0,tail)
        elif shape=='missing':self.put(head,'<3I',key^1,0,0)
        else:self.put(head,'<3I',key,found,0)
        table=self.alloc(24);self.put(table,'<6I',shift,0 if shape=='null-bucket' else buckets,0,0,0,0)
        entry=self.alloc(12);self.put(entry,'<3I',table,array_name,0)
        return entry,found,array
labels=[];COUNT=BASE+0x6901

def run(g,key,label,expected,p=()):
    stages=oracle.case([(0x45be90,PREFIX_MANAGER,[key,COUNT]),(0x45bf90,0,[key,COUNT])],g.patches()+list(p))
    assert all(s['result']==RESULTS for s in stages)
    assert int.from_bytes(oracle.cpu.mem_read(COUNT,2),'little')==len(expected)
    assert [oracle.word(RESULTS+i*4) for i in range(len(expected))]==expected,(label,expected)
    labels.append(label)

g=PrefixGraph();run(g,0,'empty manager retains result buffer',[])
for shift,key,shape in itertools.product([0,1,4,32,33,36],[0,1,3,0xffffffff],['direct','collision','null-value','missing']):
    g=PrefixGraph();entry,_,_=g.entry(key,[2,0,2,1],[0x21,None,0x33],shift,shape);g.put(PREFIX_MANAGER,'<I',entry)
    run(g,key,f'shift{shift} key{key:x} {shape}',[] if shape=='missing' else [0x33,0x21,0x33,0])
g=PrefixGraph();entry,_,_=g.entry(0,[],[],0,'null-bucket');g.put(PREFIX_MANAGER,'<I',entry);run(g,0,'null bucket',[])
for count in [0,1,2,7,1000]:
    g=PrefixGraph();entry,_,_=g.entry(7,[0]*count,[0x778899],alias=True);g.put(PREFIX_MANAGER,'<I',entry)
    run(g,7,f'count{count} inline one-node array aliased symbol',[0x778899]*count)
for first_empty in [False,True]:
    g=PrefixGraph();a,_,_=g.entry(3,[0,1],[0x10000008,9],shape='missing' if first_empty else 'direct')
    b,_,_=g.entry(3,[1,0,1],[41,42]);g.put(a+8,'<I',b);g.put(PREFIX_MANAGER,'<I',a)
    run(g,3,f'multiple arrays first missing{first_empty}',([] if first_empty else [0x10000009,9])+[42,41,42])
# MOVZX loads 16-bit node indices; they must never become signed offsets.
g=PrefixGraph();entry,found,array=g.entry(1,[32768,65535],[1]);items=g.alloc(65536*4)
node_a=g.structure([(0xa1dc81f9,13,0x123)]);node_b=g.structure([(0xa1dc81f9,13,0x456)])
g.put(items+32768*4,'<I',node_a);g.put(items+65535*4,'<I',node_b);g.put(array+4,'<2I',65536,items);g.put(PREFIX_MANAGER,'<I',entry)
run(g,1,'unsigned indices32768 and65535',[0x123,0x456])
coverage={hex(a):{'total':len(insns),'covered':sum(bool(hits[i.address]) for i in insns),'missing':[hex(i.address) for i in insns if not hits[i.address]]} for a,insns in instructions.items()}
missing={a for v in coverage.values() for a in v['missing']}
assert missing==set(),missing
scope='Two original node-prefix lookup routines45be90/45bf90 traverse already populated per-array indexes and resolve node names from script arrays. Masked hash shifts, null-valued collisions, missing/empty lists, array aliases, inline single-element storage, unsigned16-bit indices including32768/65535, duplicate names, ordering across arrays and the full1000-name result capacity compare with original instructions. Entire arena, every result word, globals, halfword count, returns and callee-saved registers match. Valid indexes and at most1000 results are original internal contracts. Index construction, native Kill and scene mutation remain unrecovered.'
fixture={'base':BASE,'memory':'node-prefix-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'pointer_exports':[[RESULTS,'thug_node_prefix_results_draft']],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'node-prefix-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'callee_calls':dict(oracle.coverage),'scope':scope}
(folder/'node-prefix-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
