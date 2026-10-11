"""Original message codecs, intrusive queues and shared payload ownership."""
import hashlib,itertools,json,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'network-queue.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x180000
CONTEXT,ADAPTER,MANAGER,DIAGNOSTICS,PRINT=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x400,BASE+0x700
CLIENT,PEERS,LINKS,SPEC,HEAD,NODES,ITER,STATE=BASE+0x1000,BASE+0x4000,BASE+0x6000,BASE+0x7000,BASE+0x7100,BASE+0x7200,BASE+0x7600,BASE+0x7700
ID,LENGTH,MESSAGE,INPUT,OUTPUT,LOG,HEAP=BASE+0x7800,BASE+0x7802,BASE+0x7900,BASE+0x10000,BASE+0x24000,BASE+0x40000,BASE+0x50000
memory=bytearray(b'\xad'*SIZE);rng=random.Random(0x457eb0)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def node(at,value=None,priority=0,previous=None,next_=None,methods=0x647578):
 put(at,'<5I',methods,at if value is None else value,priority,at if previous is None else previous,at if next_ is None else next_)
def chain(sentinel,nodes,values=None,methods=0x647578):
 node(sentinel,0xffffffff,previous=nodes[-1] if nodes else sentinel,next_=nodes[0] if nodes else sentinel,methods=methods)
 for i,at in enumerate(nodes):node(at,at if values is None else values[i],i, nodes[i-1] if i else sentinel,nodes[i+1] if i+1<len(nodes) else sentinel,methods)
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x110,'<I',MANAGER+0x300);put(MANAGER+0x124,'<I',MANAGER+0x200);put(MANAGER+0x12c,'<I',MANAGER+0x400)
put(DIAGNOSTICS,'<I',0);put(PRINT,'<2I',DIAGNOSTICS,0);put(CLIENT+8,'<I',0xfffffffa)
peers=[PEERS+i*0x500 for i in range(5)];links=[LINKS+i*20 for i in range(5)];ids=[0,1,127,0x12340001,0xffffffff]
for i,p in enumerate(peers):
 for k in range(3):node(p+k*20,0xffffffff,methods=0x6474cc+k*4)
 put(p+0x3c,'<I',ids[i]);put(p+0x60,'<I',1);put(p+0x78,'<256I',*[(0xfffffffe+g+i)&0xffffffff for g in range(256)])
chain(CLIENT+0x1e8c,links,peers)
for i in range(16):node(NODES+i*0x80)
chain(HEAD,[]);put(STATE+8,'<5I',CLIENT,0,CLIENT+4,0xabcdef01,0xffffffff)
put(SPEC,'<BBHIII4BII4B',0x31,0xc3,32,INPUT,0x87654321,0,8,0,0x76,0x98,9,0,0,0x43,0x21,0x10)
put(MESSAGE,'<BBHIII',0x31,0xad,32,INPUT,0,0)
put(ID,'<BBH',0x31,0xa7,32)
data=(bytes(range(256))*320)[:0x14000];memory[INPUT-BASE:INPUT-BASE+len(data)]=data
initial=bytes(memory);(out/'network-queue-memory.bin').write_bytes(initial)
globals_=[['thug_lzss_encoder',0x690f7c+offset,4,offset] for offset in range(0,36,4)];defaults=[0]*9
functions={}
def bind(at,name,this=False,result='void',cleanup=0,heap=False,args=None):
 f={'name':name,'this':this,'result':result,'cleanup':cleanup,'memory':heap};functions[hex(at)]=f
 if args is not None:f['stack_args']=list(range(args))
bind(0x401cc0,'thug_allocate_zeroed',result='word',heap=True)
bind(0x4549f0,'thug_message_spec_initialize',True)
bind(0x454a60,'thug_message_rle_encode',result='word')
bind(0x454e30,'thug_message_compress',result='word',heap=True,args=4)
bind(0x454fa0,'thug_message_initialize',True,'word',16,True,4)
bind(0x455040,'thug_sequenced_message_initialize',True,'word',20,True,5)
bind(0x4550f0,'thug_message_destroy',True,heap=True)
bind(0x456d90,'thug_queue_create_sequenced',True,'word',20,True,5)
for k,n in enumerate(['plain','reliable','sequenced']):
 bind([0x4555f0,0x455620,0x455650][k],'thug_'+n+'_node_initialize',True,'word',4)
 bind(0x455b50+k*0x20,'thug_'+n+'_queue_destroy',True)
 bind(0x455170+k*0x40,'thug_'+n+'_queue_delete',True,'word',4,True)
 bind(0x4557c0+k*0x30,'thug_'+n+'_node_delete',True,'word',4,True)
bind(0x457350,'thug_queue_insert',True,cleanup=4)
bind(0x54b6b0,'thug_queue_first',True,'word',4)
bind(0x457910,'thug_queue_find_peer',True,'word',4)
bind(0x457c80,'thug_queue_remove_message',True,cleanup=12,heap=True)
bind(0x457eb0,'thug_queue_enqueue',True,cleanup=8,heap=True,args=2)
bind(0x459e50,'thug_queue_send_first',True,cleanup=4,heap=True,args=1)
bind(0x532ea0,'thug_network_get_client',True,'word',4)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=30000000,
 observe=[int(k,16) for k in functions]+[0x401700],scope_entries={MANAGER+0x200:1,MANAGER+0x300:2,MANAGER+0x400:4})
pe=load();raw=pe.get_memory_mapped_image();pointer_symbols=[]
for name,s in [('sending','*** Sending compressed message %d. Old size : %d '),('rle','RLE : New payload len : %d, New size : %d\n'),
 ('lzss','LZSS : New payload len : %d, New size : %d\n'),('larger','*** Compressed message was larger. Defaulting back to uncompressed version\n')]:
 at=raw.index(s.encode()+b'\0')+0x400000;pointer_symbols.append([at,'thug_message_format_'+name,s])
formats={at:(0 if name.endswith('larger') else 2) for at,name,_ in pointer_symbols}
exports=[[0x6474cc+4*k,'thug_'+n+'_queue_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]+[[0x647578+4*k,'thug_'+n+'_node_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]
for at,fn in zip([e[0] for e in exports],[0x455170,0x4551b0,0x4551f0,0x4557c0,0x4557f0,0x455820]):assert int.from_bytes(pe.get_data(at-0x400000,4),'little')==fn
pointer_fields={at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in dict(exports)}
pointer_fields.update(DIAGNOSTICS+16+i*16 for i in range(40))
def diagnostic(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=oracle.word(sp+4);count=oracle.word(DIAGNOSTICS);argc=formats[fmt];assert count<40
 cpu.mem_write(DIAGNOSTICS+16+count*16,struct.pack('<4I',fmt,argc,oracle.word(sp+8) if argc else 0,oracle.word(sp+12) if argc else 0))
 oracle.setword(DIAGNOSTICS,count+1);cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
labels=[]
def call(at,this=0,*args):return (at,this,list(args))
def case(calls,patches=(),label='synthetic'):
 if len(labels)%500==0:print('Original queue cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,patches);callbacks=0
 for step in stages:
  merged=[]
  for at,data in step['outputs']:
   if at==DIAGNOSTICS:
    count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-callbacks;callbacks=count
   value=int.from_bytes(bytes.fromhex(data),'little')
   if value in dict(exports):pointer_fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  step['outputs']=merged
 return stages
for size in [0,1,2,3,4,5,15,16,17,28,40,44,127,128,129,4096]:case([call(0x401cc0,0,size)])
case([call(0x4549f0,SPEC),call(0x4549f0,SPEC)])
# Exhaustive short binary patterns and long run/literal transitions, including
# output alignment and the ignored capacity argument.
def rle(data,capacity=0,offset=0):
 case([call(0x454a60,0,INPUT+offset,len(data),OUTPUT+offset,capacity)],[[INPUT+offset,data.hex()]],'RLE pattern '+str(len(data)))
for n in range(10):
 for bits in itertools.product([0,255],repeat=n):rle(bytes(bits),n&3,n&3)
for n in [2,3,4,126,127,128,129,130,131,255,256,257,258,259,1024,4097]:
 for prefix in [b'',b'x',bytes(range(126)),bytes(range(127)),bytes(range(128))]:
  for tail in [b'',b'z',b'zz',b'xyz']:rle(prefix+b'\xff'*n+tail,0xffffffff,len(tail)&3)
for n in [127,128,129,255,256,257,4096,65532]:
 rle(bytes(rng.randrange(256) for _ in range(n)),0)
# Compression return/header writes, diagnostics and exact candidate allocation.
for mode in [0,1,2,3,255,256,257,258,0xffffffff]:
 for n in [0,1,2,3,4,5,6,7,8,9,16,32,129,1024]:
  for repeat in [False,True]:
   payload=bytes([0x41])*n if repeat else bytes(rng.randrange(256) for _ in range(n))
   p=[patch(ID,'<BBH',0x31,0xa7,n),[INPUT,payload.hex()]]
   case([call(0x454e30,0,ID,LENGTH,INPUT,mode,PRINT)],p,'message compression')
# Constructors retain padding and truncate id, length, group and compression.
for at in [0x454fa0,0x455040,0x456d90]:
 for mode in [0,1,2,3,256,257,258]:
  for n in [0,1,2,3,8,32,129,0x10000,0x10001]:
   args=[0x12345631,n,INPUT]+([0x123456ff] if at!=0x454fa0 else [])+[mode,PRINT]
   calls=[call(at,CLIENT if at==0x456d90 else MESSAGE,*args)]
   if at!=0x456d90:calls+=[call(0x4550f0,MESSAGE)]
   case(calls,[[INPUT,(b'A'*129).hex()]],'message construction/destruction')
case([call(0x4550f0,MESSAGE)],[patch(MESSAGE+4,'<I',0)])
# Constructors and all six virtual deletion paths on singleton/middle nodes.
for k in range(3):
 init=[0x4555f0,0x455620,0x455650][k];destroy=0x455b50+0x20*k
 case([call(init,NODES,MESSAGE),call(destroy,NODES)])
 for fn in [destroy,0x455170+k*0x40,0x4557c0+k*0x30]:
  for flags in ([0] if fn==destroy else [0,1,2,3,0x100,0x101,0xffffffff]):
   for linked in [False,True]:
    p=[]
    if linked:p=[patch(NODES+12,'<2I',HEAD,NODES+0x80),patch(HEAD+16,'<I',NODES),patch(NODES+0x80+12,'<I',NODES)]
    case([call(fn,NODES,*([] if fn==destroy else [flags]))],p+[patch(CONTEXT+24,'<I',NODES)],'node destructor and unlink')
# Priority ties and signed boundaries, reverse iteration, all insertion orders.
for priorities in [[0],[1,0xffffffff,0,0x80000000,0x7fffffff],[0]*8,[0x80,1,0x80,0,255,128,256],list(range(8)),list(range(8))[::-1]]:
 patches=[patch(NODES+i*0x80+8,'<I',v) for i,v in enumerate(priorities)]
 case([call(0x457350,HEAD,NODES+i*0x80) for i in range(len(priorities))]+[call(0x54b6b0,ITER,HEAD)],patches,'sorted list insertion')
case([call(0x54b6b0,ITER,HEAD)])
for id_ in ids+[2,128,255,0xffffff7f,0x12340000]:case([call(0x457910,CLIENT,id_)])
for which in range(5):case([call(0x532ea0,STATE,which)])
for offset in range(5):
 case([call(0x457910,CLIENT,0),call(0x457910,CLIENT,0xffffffff)],[patch(links[offset]+4,'<I',0)],'null peer value stops traversal')
# Complete queue cases cover recipient selection, each delivery, all flag
# bytes and nonzero upper flag words. Existing calls and allocation stay real.
recipients=[0,1,127,0x12340001,0xff,0x80,0x81,0x12340081,0x1ff,0xffffffff]
for delivery in [0,1,2,3,255,0xffffffff]:
 for flags in ([0,1,2,8,9,0x100,0x101,0xffffffff] if delivery<3 else [1]):
  for recipient in recipients:
   for id_ in ([9,0x31] if delivery==0 else [0x31]):
    p=[patch(SPEC,'<B',id_),patch(SPEC+12,'<I',delivery)]+[patch(peer+0x60,'<I',flags) for peer in peers]
    case([call(0x457eb0,CLIENT,recipient,SPEC,PRINT)],p,'recipient delivery and peer gating')
for flags in range(256):
 for delivery in range(3):
  case([call(0x457eb0,CLIENT,1,SPEC,PRINT)],[patch(SPEC+12,'<I',delivery),patch(peers[1]+0x60,'<I',flags)],'all peer flag bytes')
# Mixed eligibility, replacement across peers, shared payload references, signed
# priority, explicit/automatic sequence (including overflow and full byte group).
for delivery in range(3):
 for group in [0,1,8,127,255]:
  for sequence in [0,1,0x80000000,0xffffffff]:
   for recipient in [0xff,0x81,1]:
    p=[patch(SPEC+12,'<I',delivery),patch(SPEC+16,'<BB',group,1),patch(SPEC+24,'<I',sequence)]
    calls=[call(0x457eb0,CLIENT,recipient,SPEC,PRINT),call(0x457eb0,CLIENT,recipient,SPEC,PRINT)]
    calls += [call(0x457c80,CLIENT,peer,delivery,0x131) for peer in peers]
    case(calls,p,'enqueue replace and shared removal')
for mode in [1,2,3]:
 for delivery in range(3):
  for recipient in [0xff,0x81,1]:
   p=[patch(SPEC+12,'<I',delivery),patch(SPEC+28,'<B',mode),[INPUT,(b'A'*32).hex()]]
   calls=[call(0x457eb0,CLIENT,recipient,SPEC,PRINT)]+[call(0x457c80,CLIENT,peer,delivery,0x12) for peer in peers]
   case(calls,p,'compressed shared message removal')
for delivery in [0,1,2,3,0x100,0xffffffff]:
 case([call(0x457c80,CLIENT,peers[0],delivery,0x31)])
 case([call(0x459e50,CLIENT,SPEC,PRINT)],[patch(SPEC+12,'<I',delivery)],'first peer forwarding')
for empty in [True,False]:
 p=[patch(CLIENT+0x1e98,'<I',CLIENT+0x1e8c)] if empty else [patch(links[-1]+4,'<I',0)]
 case([call(0x459e50,CLIENT,SPEC,PRINT),call(0x457eb0,CLIENT,0xff,SPEC,PRINT)],p,'empty or null peer list')
# Hand-constructed queues isolate nonmatching ids, shared/underflow references,
# all concrete virtual destructors, and reverse traversal after adjacent deletes.
for delivery in range(3):
 for refs in [0,1,2,3,0xffffffff]:
  for matches in [0,1,3,7]:
   sentinel=peers[0]+delivery*20;nodes=[NODES+i*0x80 for i in range(3)];messages=[MESSAGE+i*32 for i in range(3)]
   p=[patch(sentinel+12,'<2I',nodes[-1],nodes[0])]
   for i,n in enumerate(nodes):
    p+=[patch(n,'<5I',0x647578+4*delivery,n,1,nodes[i-1] if i else sentinel,nodes[i+1] if i<2 else sentinel),
        patch(n+[20,24,40][delivery],'<I',messages[i]),patch(messages[i],'<BBHI',0x31 if matches&(1<<i) else 0x32,0x96,4,INPUT),
        patch(messages[i]+(12 if delivery==2 else 8),'<I',refs)]
   case([call(0x457c80,CLIENT,peers[0],delivery,0x31)],p,'standalone removal ownership')
scope='27 original functions: zero allocation; message descriptors, RLE and optional RLE/LZSS compression; ordinary/sequenced payload ownership; three node constructors and nine base/derived destructor entries; signed-priority insertion and reverse iteration; peer lookup, removal, shared enqueue, first-peer forwarding and network client lookup. Full recipient bits, peer eligibility, group-index boundaries, replacement, shared references, sequence/time wrap and exact padding/output/heap/global/diagnostic state are compared against unchanged x86 instructions. Original LZSS and concrete virtual destructors execute. Heap/scope services and diagnostic output are instrumented platform boundaries. Valid circular lists, existing direct recipients, successful allocation, nonoverlapping codec buffers and fitting 16-bit payloads are required. Sockets, receive/acknowledgement processing and the script scheduler are not implemented by these functions.'
fixture={'base':BASE,'memory':'network-queue-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'pointer_symbols':pointer_symbols,'pointer_exports':exports,
 'pointer_fields':sorted(pointer_fields),'native_callback':{'module':'network-diagnostics.wasm','export':'fixture_network_print','slots':[PRINT+4]},
 'callback_counter':'diagnostic_callbacks','case_labels':labels}
assert len(functions)==27,len(functions)
path=out/'network-queue-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'network-diagnostics.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/network_diagnostics.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_network_queue_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'network-queue-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
