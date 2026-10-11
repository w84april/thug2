"""Compare the complete native Change command with the original instructions."""
import hashlib,itertools,json,random,struct
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/analysis';pe=load();rng=random.Random(0x449d00)
BASE,SIZE=0x1800000,0x100000
CONTEXT,ADAPTER,MANAGER,CONTROL=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x6400
BUCKETS,LOG,HEAP=BASE+0x8000,BASE+0x40000,BASE+0x60000
initial=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,initial,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
initial[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000)
initial[CONTROL-BASE:CONTROL-BASE+32]=bytes(32);initial=bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
          ['thug_script_string_interning',0x6f3570,1],['thug_script_symbol_buckets',0x6f3624,4]]
defaults=[0,0,0,BUCKETS]
functions={'0x449d00':{'name':'thug_script_change_draft','this':False,'result':'byte','cleanup':0,'memory':True}}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
    observe=[0x476950,0x476a90,0x476490,0x478cc0,0x4711d0,0x479110,0x478cf0,0x478a60,0x478540])
instructions=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x49d00,0x24c),0x449d00))
hits=Counter();saved=[];returns={i.address for i in instructions if i.mnemonic=='ret'}
registers=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
def trace(cpu,at,size,user):
    hits[at]+=1
    if at==0x449d00:saved[:]=[cpu.reg_read(r) for r in registers]
    if at in returns:assert saved==[cpu.reg_read(r) for r in registers]
oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x449d00,end=0x449f4b)
# Reuse the existing test allocator's explicit allocation-mutation controls.
record_before=oracle.record
def record(kind,a,b,c):
    record_before(kind,a,b,c)
    if kind==1 and oracle.word(CONTROL):
        count=oracle.word(CONTROL+4)+1;oracle.setword(CONTROL+4,count)
        if count==oracle.word(CONTROL):
            for off in [8,16]:
                address=oracle.word(CONTROL+off)
                if address:oracle.setword(address,oracle.word(CONTROL+off+4))
oracle.record=record
class Graph:
    def __init__(self):self.image=bytearray(initial);self.cursor=BASE+0xc000
    def put(self,at,fmt,*values):struct.pack_into(fmt,self.image,at-BASE,*values)
    def word(self,at):return struct.unpack_from('<I',self.image,at-BASE)[0]
    def alloc(self,n):
        at=self.cursor;self.cursor=(at+n+19)&~3;assert self.cursor<BASE+0x30000;return at
    def text(self,value=b'owned/value'):
        at=self.alloc(len(value)+1);self.image[at-BASE:at-BASE+len(value)+1]=value+b'\0';return at
    def structure(self,items):
        at=self.alloc(8);nodes=[self.alloc(16) for _ in items];self.put(at,'<2I',0xabcdef01,nodes[0] if nodes else 0)
        for i,(name,kind,value) in enumerate(items):self.put(nodes[i],'<BBHIII',kind*2+(i&1),0x75,0x9876,name,value,nodes[i+1] if i+1<len(nodes) else 0)
        return at
    def array(self,kind,values):
        at=self.alloc(12);self.put(at,'<BBHII',0x57,kind,0x6789,len(values),0)
        if len(values)==1:self.put(at+8,'<I',values[0])
        elif values:
            items=self.alloc(4*len(values));self.put(items,'<'+'I'*len(values),*values);self.put(at+8,'<I',items)
        return at
    def payload(self,kind):
        if kind in [3,4]:return self.text()
        if kind in [5,6,7]:
            at=self.alloc(32);self.put(at,'<4I',0xa5a50000,0x7f812345,0xff812345,0x80000000);return at
        if kind==10:return self.structure([(11,1,0xffffffff),(12,3,self.text()),(13,12,self.array(2,[0x7f812345,0x80000000]))])
        if kind==12:return self.array(10,[self.payload(10),0,self.structure([])])
        return 0x12345678
    def symbol(self,name,kind,value,flags=0x91,filename=0x98765432):
        at=self.alloc(20);bucket=BUCKETS+(name&4095)*4
        self.put(at,'<BBH4I',flags,kind,0x4321,name,filename,value,self.word(bucket));self.put(bucket,'<I',at);return at
    def patches(self):return [[BASE+i,self.image[i:i+4].hex()] for i in range(0,0x30000,4) if self.image[i:i+4]!=initial[i:i+4]]
labels=[];KEY=0x7166a123;OTHER=0x7166b123
def run(g,params,label,p=(),repeat=2):
    stages=oracle.case([(0x449d00,0,[params,0xdeadbeef])]*repeat,g.patches()+list(p));labels.append(label);return stages
def target(g,name):
    at=oracle.word(BUCKETS+(name&4095)*4)
    while at and oracle.word(at+4)!=name:at=oracle.word(at+16)
    return at

# Scalar bits, retained changes, source order, first-match target and preserved
# source-file metadata. Old owned payloads execute their real disposal routines.
for old,new,named in itertools.product(range(14),[1,2,10,12,13,3,0,31],[False,True]):
    g=Graph();g.symbol(KEY,1,17);original=g.symbol(KEY,old,g.payload(old))
    value=g.payload(new);items=[(KEY,new,value)] if not named else [(0x60f6f242,13,KEY),(0x4b40630d,new,value)]
    params=g.structure(items);steps=run(g,params,f'old{old},new{new},named{named}')
    expected=0 if old in [7,8,9] else 1
    assert all(s['result']==expected for s in steps)
    actual=target(g,KEY);assert actual and oracle.word(actual+8)==0x98765432
    if not expected:assert actual==original
    else:assert oracle.cpu.mem_read(actual+1,1)[0]==(new if new in [1,2,10,12,13] else 0)
for kind,value in itertools.product([1,2,13],[0,1,0x7fffffff,0x80000000,0xffffffff,0x7f812345,0xff812345,*[rng.randrange(2**32) for _ in range(6)]]):
    g=Graph();g.symbol(KEY,1,3);params=g.structure([(KEY,kind,value)])
    run(g,params,f'exact scalar {kind}/{value:x}');assert oracle.word(target(g,KEY)+12)==value
for mode in ['empty','missing symbol','missing value','zero named target','protected data','name zero','duplicate source','null structure']:
    g=Graph();key=0 if mode=='name zero' else KEY
    if mode!='missing symbol':g.symbol(key,1,0,flags=0x95 if mode=='protected data' else 0x91)
    items=[(key,1,99)]
    if mode=='empty':items=[]
    elif mode=='missing value':items=[(0x60f6f242,13,key)]
    elif mode=='zero named target':items=[(key,1,99),(0x60f6f242,13,0)]
    elif mode=='duplicate source':items=[(key,1,99),(key,2,0x7f812345)]
    elif mode=='null structure':items=[(key,10,0)]
    run(g,g.structure(items),mode)
for resolve,kind,exists in itertools.product([False,True],range(14),[False,True]):
    g=Graph();g.symbol(KEY,1,1)
    if exists:g.symbol(OTHER,kind,g.payload(kind))
    items=[(KEY,13,OTHER)]+([(0,13,0x991a7bc3)] if resolve else [])
    run(g,g.structure(items),f'resolve{resolve},kind{kind},exists{exists}')
for depth in [1,2,4]:
    g=Graph();g.symbol(KEY,1,1);g.symbol(OTHER,2,0x7f812345)
    for level in range(depth):g.symbol(OTHER+level+1,13,OTHER+level)
    included=g.structure([(0x4b40630d,13,OTHER+depth),(0,13,0x991a7bc3)])
    g.symbol(0x71777000,10,included)
    run(g,g.structure([(0x60f6f242,13,KEY),(0,13,0x71777000)]),f'included value and flag,alias depth{depth}')
# The resolved symbol type is shifted through an 8-bit component tag, so its
# high bit is discarded before dispatch. Preserve that behavior for every byte.
for raw_type in range(256):
    g=Graph();g.symbol(KEY,1,0);g.symbol(OTHER,raw_type,g.payload(raw_type&127))
    run(g,g.structure([(KEY,13,OTHER),(0,13,0x991a7bc3)]),f'resolved raw type byte{raw_type}')
for array_kind,count in itertools.product([1,2,3,4,5,6,10,12,13],[0,1,3]):
    g=Graph();g.symbol(KEY,1,0);values=[g.payload(array_kind) for _ in range(count)]
    run(g,g.structure([(KEY,12,g.array(array_kind,values))]),f'array type{array_kind},count{count}')
# Source reads occur after target replacement, including allocator-induced live
# changes. Never supply dangling source payloads or invent allocator failure data.
for type in [1,2,13]:
    g=Graph();g.symbol(KEY,1,0);params=g.structure([(KEY,1,1)]);source=g.word(params+4)
    run(g,params,f'allocation changes source to{type}',[patch(CONTROL,'<6I',1,0,source,0x98767500|type*2,source+8,0xff812345)],repeat=1)
    assert oracle.word(target(g,KEY)+12)==0xff812345

missing=[hex(i.address) for i in instructions if not hits[i.address]]
allowed={0x449ecb:'array allocation failure is outside successful-allocation contract',
         0x449f1e:'structure allocation failure is outside successful-allocation contract'}
assert set(int(a,16) for a in missing)<=set(allowed),missing
coverage={'total':len(instructions),'covered':len(instructions)-len(missing),'missing':missing,
          'excluded':{a:allowed[int(a,16)] for a in missing}}
scope='Native Change449d00, the first command in the archived TR_startup script. Original lookups, symbol disposal/creation, alias resolution and deep array/structure copying run unchanged. Exact scalar/NaN bits, protected symbols, duplicate precedence, included values/flags, retained calls and source mutation during allocation are checked against all arena bytes, globals, heap records, returns and callee-saved registers. Generic successful allocation, disabled array/value pools and valid non-dangling owned graphs are internal contracts; constructor failure paths retained but not executed. Direct command comparison does not establish level startup.'
fixture={'base':BASE,'memory':'script-change-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'physics-script-outputs-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'script-change-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':{'0x449d00':coverage},'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'script-change-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['scope','callee_calls','heap_events']}),flush=True)
