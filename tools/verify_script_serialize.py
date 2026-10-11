"""Original compact script-parameter serialization, including archived values."""
import hashlib,json,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-serialize.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x700000
CONTEXT,ADAPTER,MANAGER,CALLBACK=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x400
BUCKETS,BYTE_ITEMS,HALF_ITEMS,ASSETS,LOG,OUTPUT,HEAP=BASE+0x10000,BASE+0x20000,BASE+0x22000,BASE+0x100000,BASE+0x180000,BASE+0x380000,BASE+0x400000
NATIVE=0x3f01000;memory=bytearray(b'\xad'*SIZE);cursor=0x800;rng=random.Random(0x479e20)
def alloc(size):
 global cursor
 at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xf000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(n):return struct.pack('<I',n&0xffffffff)
def text(data):
 at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def array(kind,values):
 at=alloc(12);put(at,'<BBHII',0x55,kind,0x9876,len(values),0)
 if len(values)==1:put(at+8,'<I',values[0])
 elif values:
  items=alloc(len(values)*4);put(items,'<'+'I'*len(values),*values);put(at+8,'<I',items)
 return at
def structure(entries):
 at=alloc(8);nodes=[alloc(16) for _ in entries];put(at,'<2I',0x98765432,nodes[0] if nodes else 0)
 for i,(n,k,v) in enumerate(entries):put(nodes[i],'<BBHIII',k*2+(i&1),0x75,0x4321,n,v,nodes[i+1] if i+1<len(nodes) else 0)
 return at
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
put(CALLBACK,'<8I',0,0,0,0,0,0,0,0);memory[BUCKETS-BASE:BUCKETS-BASE+16388]=bytes(16388)
short=array(13,[0x12345678,0x87654321,0]);wide=array(13,[0x11223344,0x87654321,0x80000000])
def symbol(n,k,v):
 at=alloc(20);bucket=BUCKETS+(n&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0x91,k,0x4321,n,0,v,previous);put(bucket,'<I',at);return at
symbol(0x35115a20,12,short);symbol(0x25231f42,12,wide);symbol(1,13,0x35115a20);symbol(2,1,short);symbol(3,13,0xdeadbeef)
# Larger tables exercise exact byte/half index truncation, without allocating at runtime.
for i in range(300):put(BYTE_ITEMS+i*4,'<I',0xa0000000+i)
for i in range(65538):put(HALF_ITEMS+i*4,'<I',0xb0000000+i)
strings=[text(x) for x in [b'',b'a',b'longer \xff text',b'hello\0ignored']]
pair=alloc(12);put(pair,'<3I',0xdeadbeef,0x80000000,0x7f812345)
vector=alloc(16);put(vector,'<4I',0xbeef1234,0x3f800000,0xff812345,0x7fc12345)
empty=structure([]);nested=structure([(0x12345678,1,257),(0x11223344,3,strings[2]),(0,13,0xabcdef)])
inner=array(10,[nested,empty,0]);outer=array(12,[inner,array(2,[0x7f812345,0x80000000,0x3f000000])])
values={1:0x80000000,2:0x7f812345,3:strings[2],4:strings[1],5:pair,6:vector,7:0xdeadbeef,10:nested,12:outer,13:0xfefefefe}
all_values=structure([(0x12345678 if i%3==0 else 0x11223344 if i%3==1 else 0xabcdef,k,v) for i,(k,v) in enumerate(values.items())])
component=alloc(16);target=alloc(8);put(target,'<2I',0xabcdef01,component);put(component,'<BBHIII',2,0x75,0x4321,0x12345678,0,0)
arrays={k:[array(k,[]),array(k,[v]),array(k,[v,v,v])] for k,v in values.items()}
array_target=array(0,[]);parse_target=structure([])
# Exact source tables from the installed compression QB; typed parsing runs below.
source=ROOT/'local/game-files/Game/Data/scripts/game/misc/compress.qb';data=source.read_bytes();compress_address=ASSETS
memory[ASSETS-BASE:ASSETS-BASE+len(data)]=data
compression_source={'path':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),'address':ASSETS}
compression_offsets=[]
for n in [0x35115a20,0x25231f42]:
 pos=data.index(b'\x16'+word(n));pos+=5
 while data[pos] in [1,2]:pos+=1 if data[pos]==1 else 5
 assert data[pos]==7;pos+=1
 while data[pos] in [1,2]:pos+=1 if data[pos]==1 else 5
 assert data[pos]==5;compression_offsets.append(pos)
# Known archived training definitions and boundaries from the prior token oracle.
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());token_memory=(out/tokens['memory']).read_bytes();assets=[];asset_cursor=ASSETS+0x2000
for a in tokens['assets']:
 data=token_memory[a['address']-tokens['base']:a['address']-tokens['base']+a['size']];assert hashlib.sha256(data).hexdigest()==a['sha256']
 memory[asset_cursor-BASE:asset_cursor-BASE+len(data)]=data;assets.append({**a,'original_address':a['address'],'address':asset_cursor});asset_cursor=(asset_cursor+len(data)+19)&~3
assert asset_cursor<LOG
initial=bytes(memory);(out/'script-serialize-memory.bin').write_bytes(initial)
prior=json.loads((out/'script-parser-fixtures.json').read_text());globals_=prior['globals'];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for at,value in [(0x6f3574,0),(0x6f357c,0),(0x6f3570,0),(0x6f3578,0),(0x6f3580,0),(0x6f3584,0),(0x6f3624,BUCKETS),(0x6f3530,0)]:defaults[index[at]]=value
functions={}
def bind(at,n,heap=False):functions[hex(at)]={'name':'thug_script_'+n,'this':False,'result':'word','cleanup':0,'memory':heap}
bind(0x479070,'get_global_array');bind(0x46f810,'write_word');bind(0x46f840,'write_half');bind(0x479840,'write_named_header')
bind(0x4798f0,'serialize_integer');functions['0x4798f0'].update(register_args={'ecx':0,'ebx':1},stack_args=[2,3])
bind(0x479a50,'serialize_float');functions['0x479a50'].update(register_args={'ecx':0,'edx':1,'esi':3},stack_args=[2])
for at,n in [(0x479ac0,'serialize_string'),(0x479b20,'serialize_local_string')]:
 bind(at,n);functions[hex(at)].update(register_args={'ecx':0,'eax':1},stack_args=[2,3])
bind(0x479b80,'serialize_array');bind(0x479e20,'serialize_structure');functions['0x479e20']['pointer_args']=[4]
for at in [0x471b00,0x470130]:functions[hex(at)]=prior['functions'][hex(at)]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(OUTPUT-LOG)//48,instruction_limit=100000000,
 observe=[int(k,16) for k in functions]+[0x478cf0,0x46cc30,0x46cb00,0x476490])
for at in [0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.cpu.mem_map(NATIVE,4096)
def callback(cpu,address,size,user):
 count=oracle.word(CALLBACK);mode=oracle.word(CALLBACK+4);node=oracle.word(CALLBACK+32+count*4);value=oracle.word(CALLBACK+12)
 assert count<128
 cpu.mem_write(CALLBACK+0x300+count*24,struct.pack('<2I',node,mode)+bytes(cpu.mem_read(node,16)))
 oracle.setword(CALLBACK,count+1)
 if mode==1:oracle.setword(node+8,oracle.word(node+8)^value)
 if mode==2:oracle.setword(node+12,0)
 if mode==3:cpu.mem_write(node,b'\x10')
 if mode==4:oracle.setword(node+8,0)
 if mode==5:oracle.setword(node+4,value)
 sp=cpu.reg_read(UC_X86_REG_ESP);cpu.reg_write(UC_X86_REG_EAX,0xdeadbeef);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=NATIVE,end=NATIVE)
labels=[]
def call(at,*args):return (at,0,list(args))
def case(calls,patches=(),label='synthetic'):
 if len(labels)%1000==0:print('Original cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,patches);callbacks=0
 for step in stages:
  before=callbacks
  for at,data in step['outputs']:
   if at==CALLBACK:callbacks=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=callbacks-before;step['global_float_indices']=[]
  for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
   if step['globals'][index[base]]&0xfe==4:step['global_float_indices'].append(index[base+8])
 return stages
for n in [0,1,2,3,0x35115a20,0x25231f42,0xdeadbeef]:
 for missing in [0,1,0xffffffff]:case([call(0x479070,n,missing)])
for at in [0x46f810,0x46f840]:
 for offset in range(4):
  for n in [0,1,255,256,65535,65536,0x80000000,0xffffffff,0x12345678]:case([call(at,OUTPUT+offset,n)])
# Named headers: table precedence, truncation, signed counts, inline/sparse tables.
for kind in [0,1,13,127,128,255,256,0x12345678]:
 for n in [0,0x12345678,0x87654321,0x11223344,0x80000000,0xffffffff]:case([call(0x479840,OUTPUT,kind,n)])
for count in [0,1,255,256,257,300,0x80000000,0xffffffff]:
 p=[patch(short+4,'<2I',count,0xa0000000 if count==1 else BYTE_ITEMS)]
 for i in [0,254,255,256,299]:case([call(0x479840,OUTPUT+1,13,0xa0000000+i)],p,label='byte name-table index')
for count in [0,1,255,256,65535,65536,65537,65538,0x80000000,0xffffffff]:
 p=[patch(wide+4,'<2I',count,0xb0000000 if count==1 else HALF_ITEMS)]
 for i in [0,255,256,65535,65536,65537]:case([call(0x479840,OUTPUT+3,13,0xb0000000+i)],p,label='halfword name-table index')
# Integer size selection tests exact endpoints and every capacity around output.
ints=[0,1,127,128,255,256,32767,32768,65535,65536,0x7fffffff,0x80000000,0xffff7fff,0xffff8000,0xffffff7f,0xffffff80,0xffffffff]
for n in [0x12345678,0x11223344,0xffffffff]:
 for value in ints:
  for capacity in [0,1,2,3,4,5,6,7,8,9,10]:case([call(0x4798f0,n,value,OUTPUT+1,capacity)])
# Tiny float compression, exact double threshold, negative zero and raw NaN payloads.
threshold=struct.unpack('<I',struct.pack('<f',0.0001))[0]
floats=[0,0x80000000,1,0x80000001,threshold-1,threshold,threshold+1,threshold+0x80000000,threshold+1+0x80000000,0x3f800000,0x7f800000,0xff800000,0x7f812345,0xff812345,0x7fc12345]
for n in [0x12345678,0x11223344,0xffffffff]:
 for value in floats:
  for capacity in [0,2,4,5,8,9,10]:case([call(0x479a50,OUTPUT+2,n,value,capacity)])
for at in [0x479ac0,0x479b20]:
 for value in strings:
  for n in [0x12345678,0x11223344,0xffffffff]:
   for capacity in [0,3,5,6,7,12,18,19,32]:case([call(at,value,OUTPUT,n,capacity)])
# All array types, inline storage, compound nesting and failure after header/partial text.
for kind in range(256):
 selected=arrays.get(kind,[array_target]*3)
 for count,target_array in enumerate(selected):
  patches=[] if kind in arrays else [patch(array_target,'<BBHII',0x55,kind,0x9876,count,0)]
  for capacity in ([0,2,3,4,6,7,11,15,16,17,24,32,64,256] if kind in arrays else [2,3,8]):
   case([call(0x479b80,target_array,OUTPUT,capacity,0)],patches,label='array serialization and limits')
# Every component tag and compound graph; unsupported types fail without inventing output.
for kind in range(128):
 value=values.get(kind,0xdeadbeef)
 for capacity in ([0,2,3,4,5,6,8,9,12,13,16,17,32,256] if kind in values else [0,32]):
  case([call(0x479e20,target,OUTPUT,capacity,0,0)],[patch(component,'<BBHIII',kind*2+(kind&1),0x75,0x4321,0x12345678,value,0)],label='structure tag dispatch and limits')
for s in [0,empty,nested,all_values]:
 for capacity in [0,1,2,3,5,8,16,32,64,128,512]:
  for reserved in [0,1,0xffffffff]:case([call(0x479e20,s,OUTPUT,capacity,reserved,0)],label='complete nested structure')
# Callback mutations happen before tag/name/value reads. Nested values do not callback.
nodes=[];p=struct.unpack_from('<I',memory,all_values-BASE+4)[0]
while p:nodes.append(p);p=struct.unpack_from('<I',memory,p-BASE+12)[0]
for mode in [0,1,2,3,4,5]:
 # Mutate a scalar-only graph, except passive callback coverage includes all nested types.
 s=all_values if mode==0 else nested
 selected=[];p=struct.unpack_from('<I',memory,s-BASE+4)[0]
 while p:selected.append(p);p=struct.unpack_from('<I',memory,p-BASE+12)[0]
 if mode in [1,4]:selected=selected[:1];s=target
 patches=[patch(CALLBACK+4,'<3I',mode,0,0x11223344 if mode==5 else 7),patch(CALLBACK+32,'<'+'I'*len(selected),*([component] if s==target else selected))]
 for capacity in [0,5,9,256]:case([call(0x479e20,s,OUTPUT,capacity,1,NATIVE)],patches,label='serialization callback and mutation')
# Parse the supplied game's compact-name tables with the real parser before use.
real_tables=[]
for a,offset in zip([short,wide],compression_offsets):
 patches=[patch(short+4,'<2I',0,0),patch(wide+4,'<2I',0,0)]
 stages=case([call(0x471b00,a,compress_address+offset,0),call(0x479b80,a,OUTPUT,0x80000,1)],patches,label='installed compression table parse and encode')
 # Inspect the original result to retain real counts and element checksum samples.
 after=bytearray(initial)
 for at,data in patches:after[at-BASE:at-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
 for stage in stages:
  for at,data in stage['outputs']:after[at-BASE:at-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
 count=struct.unpack_from('<I',after,a-BASE+4)[0];items=struct.unpack_from('<I',after,a-BASE+8)[0]
 checksums=[struct.unpack_from('<I',after,(a+8 if count==1 else items+i*4)-BASE)[0] for i in range(count)]
 real_tables.append({'offset':offset,'count':count,'checksums':checksums})
# Both real tables feed serialization of each ordinary archived training definition.
next_tokens={p:n for fn,p,n in tokens['cases'] if fn=='0x46f690'}
definitions=json.loads((out.parent/'script-symbols.json').read_text())['training'];training=[]
for asset in assets:
 metadata=next(a for a in definitions if a['member']==asset['member']);count=0
 for definition in metadata['definitions']:
  old=asset['original_address'];p=old+definition['offset'];q=next_tokens[p]
  while token_memory[q-tokens['base']] in [1,2]:q=next_tokens[q]
  assert token_memory[q-tokens['base']]==7;q=next_tokens[q]
  while token_memory[q-tokens['base']] in [1,2]:q=next_tokens[q]
  calls=[call(0x471b00,short,compress_address+compression_offsets[0],0),call(0x471b00,wide,compress_address+compression_offsets[1],0),
   call(0x470130,asset['address']+q-old,definition['name'],parse_target,0),call(0x479e20,parse_target,OUTPUT,0x80000,1,0)]
  stages=case(calls,[patch(short+4,'<2I',0,0),patch(wide+4,'<2I',0,0)],label='archived '+asset['member'])
  assert stages[-1]['result']>0,(asset['member'],definition)
  count+=1
 training.append({'member':asset['member'],'sha256':asset['sha256'],'definitions':count})
scope='Ten original routines: alias-aware global array lookup, unaligned word/half writers, compact named headers, compact integers, tiny-float compression, ordinary/local strings, and mutually recursive array/structure serialization. Full fixture/global bytes, buffer partial writes, return values and callbacks compared to original x86, with exact raw NaN payload serialization. Original concrete symbol/array/parser callees execute; only generic heap services and configured serialization callbacks are instrumented. Tests cover size/tag boundaries, unsupported types, signed table counts, truncated byte/half name indexes, nested graphs and callback mutation/suppression; the supplied compression QB is parsed and its actual tables used to encode all 164 ordinary definitions from eight archived training QB files. This is parameter encoding, not network message delivery, frame scheduling, spawn, gameplay or rendering.'
fixture={'base':BASE,'memory':'script-serialize-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_symbols':prior['pointer_symbols'],'pointer_globals':prior['pointer_globals'],
 'callback_counter':'serialization_callbacks','native_callbacks':[{'module':'script-serialize-callback.wasm','export':'fixture_serialize_callback','original':NATIVE}],
 'compression_source':compression_source,'compression_tables':real_tables,'training':training}
path=out/'script-serialize-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
adapter=out/'script-serialize-callback.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_serialize_callback.c'),'-o',str(adapter)],check=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_serialize_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'compression_source':compression_source,'compression_tables':real_tables,'training':training,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-serialize-memory.bin',adapter,out/'script-values-memory.wasm',source]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
