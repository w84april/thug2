"""Execute original texture parsing unchanged, adapting only heap/GPU ports."""
import hashlib,json,struct,subprocess
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/analysis';BASE,SIZE=0x1800000,0x200000
ADAPTER,CONTEXT,MANAGER=BASE+0x100,BASE+0x200,BASE+0x400
P,INPUT,CURSOR,DEVICE,DVT,TVT,CONTROL,GLOG= [BASE+n for n in [0x8000,0xa000,0x9000,0x10000,0x11000,0x11200,0x12000,0x14000]]
LOG,HEAP,TEXTURES=BASE+0x40000,BASE+0x60000,BASE+0x100000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
put(CONTEXT,'<8I',HEAP,TEXTURES,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(DEVICE,'<I',DVT);put(CONTROL,'<3I',0,0,0x1234)
initial=bytes(memory);pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
specs=[(0x49fd30,94,'object_table_clear',0,'void',True,True),
 (0x49f830,182,'texture_dictionary_base_construct',2,'word',True,True),
 (0x4c8070,27,'texture_dictionary_construct',1,'word',True,True),
 (0x4e04b0,78,'texture_resource_construct',0,'word',True,True),
 (0x49f200,15,'texture_wrapper_base_construct',0,'word',False,True),
 (0x4cb420,823,'texture_buffer_parse',3,'word',True,False),
 (0x4cb7c0,145,'texture_dictionary_load_buffer',1,'byte',True,True),
 (0x4c72e0,126,'texture_dictionary_create_buffer',7,'word',True,False),
 (0x49f010,61,'texture_dictionary_cached',1,'word',False,False),
 (0x49f050,110,'texture_dictionary_get_buffer',7,'word',True,False)]
functions={hex(a):{'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap} for a,n,name,argc,result,heap,this in specs}
globals_=[['thug_texture_resource_registry_draft',0x7cc254,4],['thug_mesh_device',0x7d69e0,4],['thug_lookup_node_pool',0x7d1808,4]]
defaults=[0,DEVICE,0]
for i in range(6):globals_.append(['thug_model_texture_table_draft',0x700f04+i*4,4,i*4]);defaults.append(0)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,scope_entries={MANAGER+0x200:1},
 observe=[a for a,*_ in specs]+[0x49fd90,0x462740,0x5ba090,0x588190])
fields={P};exports=[[0x649bb4,'thug_texture_dictionary_base_methods_draft'],[0x64a824,'thug_texture_dictionary_pc_methods_draft'],[0x649af0,'thug_texture_wrapper_base_methods_draft'],[0x64a770,'thug_texture_wrapper_pc_methods_draft']]
original_record=oracle.record
def record(kind,a,b,c):
    if kind==1:oracle.setword(c-16,MANAGER+0x200)
    log=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48;ptr=a if kind==2 else c
    for i in range(4):
        if ptr+i*4 in fields:fields.add(log+16+i*4)
    original_record(kind,a,b,c)
oracle.record=record
def identity(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX))
for a in [0x49f830,0x4c8070,0x49f200]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=a,end=a)
code={a:list(md.disasm(pe.get_data(a-0x400000,n),a)) for a,n,*_ in specs};hits=Counter()
for a,n,*_ in specs:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
CREATE,LOCK,UNLOCK=oracle.stop+0x300,oracle.stop+0x310,oracle.stop+0x320
gpu_counts=Counter()
def gpu(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
    op={CREATE:1,LOCK:2,UNLOCK:3}[at];i=oracle.word(CONTROL);assert i<200
    oracle.setword(CONTROL,i+1);log=[op]+[0]*14+[oracle.word(CONTEXT+8)]
    if op==1:
        args=[arg(k) for k in range(9)];count=oracle.word(CONTROL+4);assert count<32
        p=TEXTURES+count*0x1000;oracle.setword(CONTROL+4,count+1)
        oracle.setword(p,TVT);oracle.setword(args[7],p);log[1:11]=args+[p];argc=9
    elif op==2:
        p,level,out,rect,flags=[arg(k) for k in range(5)];assert level<8
        data=p+0x100+level*0x100;pitch=oracle.word(CONTROL+8)
        oracle.setword(out,pitch);oracle.setword(out+4,data);log[1:7]=[p,level,rect,flags,pitch,data];argc=5
    else:log[1:3]=[arg(0),arg(1)];argc=2
    cpu.mem_write(GLOG+i*64,struct.pack('<16I',*log));gpu_counts[op]+=1
    cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for a in [CREATE,LOCK,UNLOCK]:oracle.cpu.hook_add(UC_HOOK_CODE,gpu,begin=a,end=a)
labels=[];assets=[]
def call(a,this=0,args=()):return a,this,list(args)
class Graph:
    def __init__(self):
        self.data=bytearray(initial);self.next=BASE+0x20000
        self.put(DVT+0x5c,'<I',CREATE);self.put(TVT+0x4c,'<2I',LOCK,UNLOCK)
    def put(self,at,fmt,*v):struct.pack_into(fmt,self.data,at-BASE,*v)
    def alloc(self,n):
        p=self.next;self.next=(p+n+19)&~3;assert self.next<LOG;self.put(p-16,'<I',MANAGER+0x200);return p
    def table(self,entries=(),shift=2,chain=False):
        t=self.alloc(24);b=self.alloc((1<<shift)*12);self.put(t,'<6I',shift,b,len(entries),0x12345678,0x87654321,0xabcdef01)
        self.data[b-BASE:b-BASE+(1<<shift)*12]=bytes((1<<shift)*12)
        for k,v in entries:
            head=b+(k&((1<<shift)-1))*12
            if self.word(head+4) or chain:
                node=self.alloc(12);self.put(node,'<3I',k,v,self.word(head+8));self.put(head+8,'<I',node)
            else:self.put(head,'<2I',k,v)
        return t
    def word(self,p):return struct.unpack_from('<I',self.data,p-BASE)[0]
    def file(self,data):
        assert len(data)<0x6000;self.data[INPUT-BASE:INPUT-BASE+len(data)]=data;self.put(CURSOR,'<I',INPUT)
    def patches(self):return [[BASE+i,self.data[i:i+4].hex()] for i in range(0,SIZE,4) if self.data[i:i+4]!=initial[i:i+4]]
def run(g,calls,label,cache=None,registry=0):
    changes={0:registry}
    if cache is not None:
        for i in range(6):changes[3+i]=g.word(cache+4*i)
    registers=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
    before=[oracle.cpu.reg_read(r) for r in registers]
    try:stages=oracle.case(calls,g.patches(),changes)
    except Exception:print('FAILED',label,flush=True);raise
    assert before==[oracle.cpu.reg_read(r) for r in registers],label
    labels.append(label)
    known={a for a,*_ in exports}
    for step in stages:
        for a,v in step['outputs']:
            if int.from_bytes(bytes.fromhex(v),'little') in known:fields.add(a)
    return stages
def datafile(rows,version=1,count=None):
    data=struct.pack('<2I',version,len(rows) if count is None else count)
    for key,w,h,depth,compression,mips in rows:
        data+=struct.pack('<8I',key,w,h,len(mips),depth,32,compression,0)
        for mip in mips:data+=struct.pack('<I',len(mip))+mip
    return data
for fill in [0,0xa5,0xff]:
    for flag in [0,1,255,256,257]:
        g=Graph();g.data[P-BASE:P-BASE+20]=bytes([fill])*20
        run(g,[call(0x49f830,P,[0xabcdef12,flag])]*2,f'base constructor poison{fill}/flag{flag}')
    g=Graph();g.data[P-BASE:P-BASE+32]=bytes([fill])*32
    run(g,[call(0x4c8070,P,[0x12345678]),call(0x49f200,P)],f'PC and wrapper ctor poison{fill}')
for populated in [False,True]:
    g=Graph();node=g.alloc(12);g.put(node,'<3I',P+64,0,0)
    run(g,[call(0x4e04b0,P),call(0x4e04b0,P+32)],f'resource list existing{populated}',registry=node if populated else 0)
for entries,chain in [((),False),([(1,P),(5,P+4),(9,0),(2,P+8)],False),([(1,0),(5,P)],True)]:
    g=Graph();t=g.table(entries,chain=chain)
    run(g,[call(0x49fd30,t)]*2,f'table clear {entries}/chain{chain}')
g=Graph();t=g.table();g.put(t+4,'<I',0);run(g,[call(0x49fd30,t)],'absent table clear retains count')
for count in [0,0xffffffff,0x80000000]:
    g=Graph();g.file(datafile([],count=count));g.put(P+12,'<I',0)
    run(g,[call(0x4cb7c0,P,[INPUT])],f'null table signed count {count}')
    g=Graph();g.file(datafile([],count=count));t=g.table()
    run(g,[call(0x4cb420,args=[CURSOR,t,1])],f'rebuilt table signed count/shift cap {count}')
for count in [0,1,2,3,8]:
    for rebuild in [0,1,256,257]:
        rows=[(i*4+1,8,4,32,1,[bytes(range(5)),b'abc']) for i in range(count)]
        g=Graph();g.file(datafile(rows));t=g.table([(3,P+512)] if not(rebuild&255) else [(3,0),(7,0)],chain=True)
        run(g,[call(0x4cb420,args=[CURSOR,t,rebuild])],f'parser count{count}/rebuild{rebuild}')
        assert oracle.word(CURSOR)==INPUT
for compression,depth in [(0,8),(0,16),(0,32),(1,32),(2,32),(5,32),(257,0x120)]:
    for size in [0,1,2,3,4,5,17]:
        g=Graph();t=g.table();g.file(datafile([(7,0x10008,0x20004,depth,compression,[bytes(range(size))])],version=0xfefefefe))
        run(g,[call(0x4cb420,args=[CURSOR,t,0])],f'format{compression}/depth{depth}/copy{size}')
for shape in ['empty','nonempty','null head chain','null first chain']:
    g=Graph();g.file(datafile([(7,8,8,32,1,[b'abcde'])]));t=g.table([] if shape=='empty' else [(3,0 if shape=='null first chain' else P+256)],chain=shape.startswith('null'))
    g.put(P+12,'<I',t);run(g,[call(0x4cb7c0,P,[INPUT])]*2,f'dictionary table {shape}')
for rebuild in [0,1,256]:
    for compression,depth in [(0,24),(3,32)]:
        g=Graph();t=g.table();g.file(datafile([(5,8,8,depth,compression,[]),(7,8,8,32,1,[]),(9,8,8,depth,compression,[])]))
        # The PC parser does not consume palette bytes even when this header is
        # nonzero. Observe the original behavior without inventing palette I/O.
        g.put(INPUT+36,'<I',17)
        run(g,[call(0x4cb420,args=[CURSOR,t,rebuild])],f'zero mips/unknown format scratch/palette {rebuild}/{compression}/{depth}')
for shape in ['empty','head','collision','null head','absent zero bucket']:
    g=Graph();t=g.table([] if shape in ['empty','absent zero bucket'] else [(3,P),(7,P+32)],chain=shape=='null head')
    if shape=='absent zero bucket':g.put(t,'<2I',0,0)
    run(g,[call(0x49f010,args=[0 if shape=='absent zero bucket' else k]) for k in [3,7,11]],'cache '+shape,cache=t)
letter=ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.tex.xbx'
data=letter.read_bytes();assert hashlib.sha256(data).hexdigest()=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
for mode in ['parse','construct','get twice','colliding cache','wrapping key','extend']:
    g=Graph();g.file(data);t=g.table();cache=g.table([(3,P+256)] if mode=='colliding cache' else [])
    key,offset=(0xffffffff,8) if mode=='wrapping key' else (3,0)
    if mode=='parse':calls=[call(0x4cb420,args=[CURSOR,t,1])]
    elif mode=='construct':calls=[call(0x4c72e0,args=[key,INPUT,len(data),0x12345678,offset,0x100,0xffffffff])]
    elif mode=='extend':
        g.put(P+12,'<I',t);calls=[call(0x4cb7c0,P,[INPUT])]*2
    else:calls=[call(0x49f050,args=[key+(4 if mode=='colliding cache' else 0),INPUT,len(data),0,offset,0,0])]*2
    run(g,calls,'actual Letter S '+mode,cache=cache)
    n=oracle.word(CONTROL+4);assert n==(2 if mode=='extend' else 1)
    for i in range(n):
        assert bytes(oracle.cpu.mem_read(TEXTURES+i*0x1000+0x100,32))==data[44:76]
        assert bytes(oracle.cpu.mem_read(TEXTURES+i*0x1000+0x200,8))==data[80:88]
    events=[struct.unpack('<16I',oracle.cpu.mem_read(GLOG+i*64,64)) for i in range(oracle.word(CONTROL))]
    assert all(e[2:8]==(8,8,2,0,0x31545844,1) for e in events if e[0]==1)
    assets.append({'mode':mode,'path':str(letter.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'textures_created':n,'gpu_events':len(events)})
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()}
print('MISSING',json.dumps(missing),flush=True)
# Filled with explicit contract/padding exclusions after reviewing coverage.
excluded={hex(a):'initialized allocator bypasses process bootstrap' for a in [0x49f86c,0x4e04ca,0x4cb4d4,0x4cb539,0x4cb6bd,0x4c72ff]}
excluded.update({hex(a):'successful internal heap allocation contract' for a in [0x49f8b2,0x49f8b4,0x49f8b7,0x49f8b9,0x49f8bd,0x49f8c4,0x49f8c5,0x49f8c8,0x4cb504,0x4cb56a,0x4cb703,0x4c7336]})
excluded['0x4cb7da']='unreachable alignment after unconditional jump'
assert {s for values in missing.values() for s in values}==set(excluded)
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':missing[hex(a)],'excluded':{s:excluded[s] for s in missing[hex(a)] if s in excluded}} for a,c in code.items()}
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'texture-buffer-ports.c';output=folder/'texture-buffer-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
scope='Nine additional texture-buffer routines and the previously recovered table clearer with real dictionary/resource construction, ownership registry, table clearing, parsing, cache lookup and insertion. Exact whole-arena/global/heap/GPU-upload comparisons use successful bounded internal buffers and explicit initialized heap/GPU ports. A comparison-only GPU accepts create/lock/unlock and records parameters plus exact uploaded bytes; it is not a renderer. The unchanged88-byte Letter S file is parsed through six paths, yielding8x8 DXT1 with2mips and exact32/8-byte payloads. Model loader, asset file routing, GPU display and playable training level remain pending.'
fixture={'base':BASE,'memory':'texture-buffer-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm',
 'memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,
 'pointer_initializers':[['thug_texture_allocation_scope_draft',oracle.stop+0x330]],
 'native_callbacks':[{'module':'texture-buffer-ports.wasm','export':'fixture_texture_'+name,'slots':slots,**({'original':oracle.stop+0x330} if name=='scope' else {})} for name,slots in [('create',[DVT+0x5c]),('lock',[TVT+0x4c]),('unlock',[TVT+0x50]),('scope',[])]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'texture-buffer-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'existing_dependency_addresses':['0x49fd30'],'new_functions':9,'assets':assets,'gpu_calls':dict(gpu_counts),'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'texture-buffer-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['scope','assets','callee_calls','heap_events','instruction_coverage']}))
