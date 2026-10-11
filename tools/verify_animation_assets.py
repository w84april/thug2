"""Original x86 comparisons for the balance animation controller and asset lookup."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_objective_notifications.py').read_text().split('rng=random.Random(0x557360)')[0]
exec(compile(prefix.replace("'objective-notifications.json'","'animation-assets.json'").replace('Original objective notification cases:','Original animation asset cases:'),str(Path(__file__).with_name('verify_objective_notifications.py')),'exec'))
NEW=[
 (0x5b9770,'thug_async_swap_completions',0,'void',False,False,False),
 (0x5b68c0,'thug_async_process_completions',0,'void',False,False,False),
 (0x5b6a50,'thug_async_wait',1,'void',False,True,False),
 (0x407910,'thug_asset_initialize',0,'word',False,False,True),
 (0x4071a0,'thug_animation_asset_initialize',0,'word',False,False,True),
 (0x590250,'thug_asset_data',0,'word',False,False,True),
 (0x407610,'thug_asset_ready',0,'byte',False,False,True),
 (0x407680,'thug_asset_read_finished',0,'byte',False,False,True),
 (0x4076a0,'thug_asset_mark_ready',0,'byte',False,False,True),
 (0x407710,'thug_asset_read_callback',5,'void',False,False,False),
 (0x407c00,'thug_asset_find',2,'word',False,True,True),
 (0x48cf50,'thug_animation_find',2,'word',False,True,False),
 (0x48cf70,'thug_animation_reader_initialize',0,'word',False,False,True),
 (0x4b3990,'thug_animation_reader_allocate',0,'word',True,False,False),
 (0x48bfc0,'thug_create_animation_reader',0,'word',True,False,False),
 (0x48cfa0,'thug_animation_reader_set_mode',1,'word',False,True,True),
 (0x48cfd0,'thug_animation_reader_select',1,'word',False,True,True),
 (0x481650,'thug_animation_timeline_initialize',0,'word',False,False,True),
 (0x481430,'thug_animation_set_timeline',6,'void',False,False,True),
 (0x481710,'thug_animation_controller_initialize',1,'word',False,False,True),
 (0x481730,'thug_animation_controller_destroy',0,'void',False,False,True),
 (0x481740,'thug_animation_controller_configure',1,'void',False,False,True),
 (0x4819d0,'thug_animation_channel_body',0,'word',False,False,True),
 (0x481760,'thug_animation_controller_body',0,'word',False,False,True),
 (0x419ab0,'thug_animation_component_namespace',0,'word',False,False,True),
 (0x419ad0,'thug_animation_component_events',0,'word',False,False,True),
 (0x4a49f0,'thug_balance_animation_initialize',1,'word',True,True,True),
 (0x4a4af0,'thug_balance_animation_command',3,'word',False,True,True)]
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
functions['0x481430']['float_args']=[1,2,4,5]
for at in [0x476950,0x4766d0,0x476630,0x5ba3d0]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
AM,AT,AB,ASSET,ASSET2,CHANNEL,CONTROLLER,ACOMP,ASTATE,READER,AFILES,APOOL,ABLOCKS,CONTROL=[BASE+x for x in [0x1c0000,0x1c0100,0x1c0200,0x1c0400,0x1c0500,0x1c0800,0x1c0900,0x1c0a00,0x1c0b00,0x1c2000,0x1c4000,0x1c6000,0x1c6200,0x1c8000]]
memory[AM-BASE:CONTROL+0x1000-BASE]=bytes(CONTROL+0x1000-AM)
put(AM+0x1c,'<I',AT);put(AT,'<2I',3,AB)
put(AB+36,'<3I',0x123,ASSET,0)
put(ASSET,'<5I',0x6454b0,0x11111111,4,0xcccccccc,BASE+0x1c1000)
put(ASSET2,'<5I',0x6454b0,0x22222222,4,0xcccccccc,BASE+0x1c1100)
put(CHANNEL+0x14,'<3f',-10,5,30);put(CHANNEL+0x64,'<I',BODIES)
put(CONTROLLER,'<2I',0x649f80,CHANNEL);put(CONTROLLER+0x2c,'<3I',READER,0xabcdef12,0)
put(BODIES+0x100,'<I',ACOMP);put(ACOMP+4,'<I',0x7149b753);put(ACOMP+0x34,'<I',ASTATE)
put(ASTATE+0x50,'<3I',0x90000000,0,0xabc123)
put(READER,'<2I',0x648a68,0x123)
put(PRINT,'<2I',CONTROL,0)
put(APOOL,'<6I',ABLOCKS,ABLOCKS+0x900,0,0,0,ABLOCKS)
for i in range(4):put(ABLOCKS+i*0x220,'<I',ABLOCKS+(i+1)*0x220 if i<3 else 0)
for i in range(16):put(AFILES+i*64+8,'<3I',0x407710,ASSET+i%2*0x100,0)
fields.update([ASSET,ASSET2,CHANNEL,CONTROLLER,READER,CONTROL+4])
fields.update(AFILES+i*64+8 for i in range(16))
exports += [[0x6454b0,'thug_animation_asset_methods'],[0x645568,'thug_asset_base_methods'],[0x6455c0,'thug_asset_link_methods'],[0x648a68,'thug_animation_reader_methods'],[0x648768,'thug_animation_channel_base_methods'],[0x64877c,'thug_animation_controller_base_methods'],[0x649f80,'thug_balance_animation_methods'],[0x7cf180,'thug_async_completed']]
def identity(cpu,address,size,user):
 at=cpu.reg_read(UC_X86_REG_ECX);fields.add(at)
 if address in [0x407910,0x4071a0]:fields.add(at+0x38)
for at in [0x407910,0x4071a0,0x48cf70,0x481650,0x481710,0x481730,0x4a49f0]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
def addglobal(name,at,value=0,width=4,offset=0):
 assert at not in index,hex(at)
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
addglobal('thug_asset_manager',0x6918dc,AM)
addglobal('thug_animation_reader_pool_index',0x6fa7f4)
for i in range(2):addglobal('thug_animation_reader_pools',0x6fa7fc+4*i,offset=4*i)
addglobal('thug_async_pending',0x7cf17c)
addglobal('thug_async_completed',0x7cf180,width=1)
addglobal('thug_async_write_buffer',0x7cf18c)
for i in range(2):addglobal('thug_async_completion_counts',0x7cf184+4*i,offset=4*i)
for i in range(16):addglobal('thug_async_files',0x7cf138+4*i,AFILES+i*64,offset=4*i)
for i in range(96):addglobal('thug_async_completions',0x7cefb8+i*4,offset=i*4)
initial=bytes(memory);oracle.initial=initial

# Keep the actual file callback, readiness and data methods. Only diagnostic
# output is intercepted. Optional writes model an external I/O/asset producer,
# explicitly separate from the recovered callback (which reaches state 2).
diagnostics=Counter()
def debug_output(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ptr=oracle.word(sp+4)
 text=bytes(cpu.mem_read(ptr,120)).split(b'\0')[0]
 kind=1 if text.startswith(b'CAsyncFileLoader waiting ') else 2 if text.startswith(b'CAsyncFileLoader got ') else 3
 assert text in [b'CAsyncFileLoader waiting for io completion: busy count %d completion %d\n',b'CAsyncFileLoader got completion: busy count %d completion %d\n',b'CAsyncFileLoader still needs to wait for file handle %d\n'],text
 n=oracle.word(CONTROL);assert n<32;oracle.setword(CONTROL,n+1)
 h=0
 for c in text:h=(h*33+c)&0xffffffff
 state=oracle.word(CONTROL+8)
 cpu.mem_write(CONTROL+64+n*32,struct.pack('<8I',h,kind,oracle.word(sp+8),oracle.word(sp+12) if kind!=3 else 0,oracle.word(state) if state else 0,0,0,0))
 if kind==1 and oracle.word(CONTROL+4):cpu.mem_write(oracle.word(CONTROL+4),b'\x01')
 if state and n==oracle.word(CONTROL+12):oracle.setword(state,4)
 if oracle.word(CONTROL+16) and n==oracle.word(CONTROL+24):oracle.setword(oracle.word(CONTROL+16),oracle.word(CONTROL+20))
 diagnostics[kind]+=1
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
# A fresh oracle excludes the inherited score-specific diagnostic hook.
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=2000000,scope_entries={ALLOCATOR+0x200:6,ALLOCATOR+0x300:1,ALLOCATOR+0x500:5,ALLOCATOR+0x600:4})
oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,begin=0x401c30,end=0x401c30)
for at in [0x407910,0x4071a0,0x48cf70,0x481650,0x481710,0x481730,0x4a49f0]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
heap_record=oracle.record;oracle.record=relocated_record
old_case=case
def case(calls,patches=(),changes=None,label='animation assets'):
 stages=old_case(calls,patches,changes,label);previous=0;quiet=[];arithmetic=[]
 for s in stages:
  for at,data in s['outputs']:
   if at<=CONTROL and at+len(data)//2>=CONTROL+4:
    current=int.from_bytes(bytes.fromhex(data)[CONTROL-at:CONTROL-at+4],'little');s['callbacks']=current-previous;previous=current
  if s['fn']=='0x481430' or (s['fn']=='0x4a4af0' and s['args'][0]==0xaf2fae19):
   quiet=[CHANNEL+0x14,CHANNEL+0x1c];arithmetic.append(CHANNEL+0x20)
  if s['fn']=='0x4a4af0' and s['args'][0]==0xd0209498:arithmetic.append(CONTROLLER+0x28)
  s['float_fields']=sorted(set(arithmetic))
  s['quiet_float_fields']=quiet
 return stages
rng=random.Random(0x4a4af0)

for _ in range(16):
 p=[raw(at,bytes(rng.getrandbits(8) for _ in range(n))) for at,n in [(ASSET,0x50),(ASSET2,0x50),(CHANNEL,0x74),(CONTROLLER,0x38),(READER,0x214)]]
 case([call(0x407910,ASSET),call(0x4071a0,ASSET2),call(0x481650,CHANNEL),call(0x481710,CONTROLLER,[CHANNEL]),call(0x481730,CONTROLLER),call(0x48cf70,READER)],p,label='constructors preserve every unwritten byte')
for value in [0,1,2,3,4,5,255,256,0x80000000,0xffffffff]+[rng.getrandbits(32) for _ in range(22)]:
 p=[patch(ASSET+8,'<I',value),patch(ASSET+0x10,'<I',value),patch(CHANNEL+0x64,'<I',value),patch(ASTATE+4,'<I',value),patch(ASTATE+0x50,'<I',value^0x12345),patch(ASTATE+0x58,'<I',value^0x34567)]
 case([call(0x590250,ASSET),call(0x407610,ASSET),call(0x407680,ASSET),call(0x407610,ASSET),call(0x4076a0,ASSET),call(0x407610,ASSET),call(0x4819d0,CHANNEL),call(0x481760,CONTROLLER),call(0x419ab0,ACOMP),call(0x419ad0,ACOMP)],p,label='stored values, real readiness states and sentinel getters')
for value in [None,0,1,0x80000000,0xffffffff]:
 for kind in [1,13,2]:
  b=Build();p=b.structure([] if value is None else [(0x40c698af,kind,value)])
  case([call(0x481740,CONTROLLER,[p])],b.patches()+[patch(CONTROLLER+0x10,'<I',0xaabbccdd)],label='optional controller name, presence and type')
special=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f800001]
for i in range(220):
 a,b=(rng.choice(special),rng.choice(special)) if i<100 else (rng.getrandbits(32),rng.getrandbits(32))
 speed=rng.choice(special) if i<100 else rng.getrandbits(32)
 case([call(0x481430,CHANNEL,[rng.getrandbits(32),a,b,rng.getrandbits(32),rng.getrandbits(32),speed])],label='timeline endpoints, direction, raw current and PC24 speed')

# Pools include both indices, empty pools, and the real heap fallback.
for pool_index in [0,1]:
 for mode in ['heap','pool','empty']:
  p=[patch(APOOL+20,'<I',0)] if mode=='empty' else []
  changes={0x6fa7f4:pool_index,0x6fa7fc+pool_index*4:0 if mode=='heap' else APOOL}
  case([call(0x4b3990),call(0x48bfc0)],p,changes,label='reader factory '+mode)
 for sentinel in [False,True]:
  case([call(0x4a49f0,CONTROLLER,[CHANNEL])],[patch(ASTATE+4,'<I',0xffffffff if sentinel else 0)],{0x6fa7f4:pool_index,0x6fa7fc+pool_index*4:APOOL},label='complete balance controller constructor with concrete reader factory')

# Exact inlined asset table traversal, including null heads and null values.
for shift in [0,2,3,32,34,35]:
 for key in [0,1,0x123,0xffffffff]:
  bucket=AB+(key&((1<<(shift&31))-1))*12
  for shape in ['direct','collision','null-value','missing']:
   p=[raw(AB,bytes(0x100)),patch(AT,'<I',shift),patch(bucket,'<3I',key if shape in ['direct','null-value'] else key^1,ASSET if shape=='direct' else 0,AB+0x80 if shape!='missing' else 0),patch(AB+0x80,'<3I',key,ASSET2,0),patch(READER+4,'<I',key)]
   case([call(0x407c00,AM,[key,1]),call(0x48cf50,args=[key,0]),call(0x48cfa0,READER,[0]),call(0x48cfd0,READER,[key])],p,label='asset table '+shape+' masked shift '+str(shift))
case([call(0x407c00,AM,[0,1])],[patch(AT,'<2I',0,0)],label='null first bucket pointer')
for mode in [0,1,255,256,257,0xffffff00,0xffffffff]:
 case([call(0x48cfa0,READER,[mode])],label='reader mode uses low byte')

# Complete controller handler, including required setup, optional groups,
# aliases, integers converted to float, unknown commands, and missing values.
for i in range(120):
 b=Build();name=0x123
 a,z=(rng.choice(special),rng.choice(special)) if i<40 else (bits(rng.uniform(-100,100)),bits(rng.uniform(-100,100)))
 p=b.structure([(0x6c2bfb7f,13,name),(0xd16b61e6,2,a),(0xab81bb3d,2,z),(0xcd8d7c1b,1,i),(0x8f0d24ed,2,bits(-999)),(0xf0d90109,2,rng.choice(special))])
 extra=[patch(CONTROLLER+0x34,'<I',0xfffffff0 if i&1 else 0),patch(AB+36,'<I',(name+(0xfffffff0 if i&1 else 0))&0xffffffff)]
 # A shifted namespace changes the bucket too; move the sole entry accordingly.
 key=(name+(0xfffffff0 if i&1 else 0))&0xffffffff
 extra += [patch(AB+(key&7)*12,'<3I',key,ASSET,0)]
 case([call(0x4a4af0,CONTROLLER,[0xaf2fae19,p,0]),call(0x4a4af0,CONTROLLER,[0x5f495ae0,p,0])],b.patches()+extra,label='full animation setup and reader refresh')
for i in range(160):
 b=Build();value=rng.choice(special) if i<80 else bits(rng.uniform(-4,4))
 entries=[] if i%9==0 else [(0x4d747fa0,1,(i-80)&0xffffffff)] if i%9==1 else [(0x4d747fa0,2,value)]
 p=b.structure(entries);a,z=(rng.choice(special),rng.choice(special)) if i<60 else (bits(rng.uniform(-100,100)),bits(rng.uniform(-100,100)))
 case([call(0x4a4af0,CONTROLLER,[0xd0209498,p,0])],b.patches()+[patch(CHANNEL+0x14,'<I',a),patch(CHANNEL+0x1c,'<I',z)],label='normalized animation position, clamps, missing values and PC24 nonfinite arithmetic')
curve_names=[0xfd266a26,0x642f3b9c,0x0f43fd49,0x964aacf3,0xf90b0824]
for missing in range(6):
 for kind in [1,2,13,10]:
  b=Build();entries=[]
  for i,n in enumerate(curve_names):
   if i==missing:continue
   value=rng.getrandbits(32)
   if kind==13:b.symbol(0xabc000+i,2,value);value=0xabc000+i
   if kind==10:value=b.structure([])
   entries.append((n,kind,value))
  p=b.structure(entries)
  case([call(0x4a4af0,CONTROLLER,[0xea6d0efd,p,0])],b.patches(),label='five optional values commit atomically; missing/type/alias')
for command in [0,0x5f495adf,0x5f495ae1,0xaf2fae18,0xaf2fae1a,0xd0209497,0xd0209499,0xea6d0efc,0xea6d0efe,0xffffffff]:
 case([call(0x4a4af0,CONTROLLER,[command,0,0])],label='unknown animation command returns two')

def completion_changes(buffer,count,argument=0):
 changes={0x7cf18c:buffer,0x7cf184+4*buffer:count,0x7cf17c:count,0x7cf180:1}
 p=[]
 for i in range(count):
  file=AFILES+(i%4)*64
  for k,v in enumerate([file,0x100+i,0x200+i]):changes[0x7cefb8+buffer*192+i*12+k*4]=v
 for i in range(4):p += [patch(AFILES+i*64+0x10,'<I',argument),patch(AFILES+i*64+0x18,'<I',0xdeadbeef),patch(AFILES+i*64+0x38,'<I',(count+3-i)//4)]
 return p,changes
for buffer in [0,1]:
 case([call(0x5b9770)],changes={0x7cf18c:buffer,0x7cf180:255},label='completion buffer swap and flag reset')
 for count in [0,1,3,4,16]:
  for argument in [0,1,0xffffffff]:
   p,ch=completion_changes(buffer,count,argument)
   case([call(0x5b68c0)],p,ch,label='real animation asset completion callbacks across both I/O buffers')
 for flag in [0,1,256,257,0xffffff00]:
  p,ch=completion_changes(buffer,4)
  case([call(0x5b6a50,args=[flag])],p,ch,label='wait pumps callbacks and scans all file slots by low-byte flag')
for arg in [0,1,255,256,0xffffffff]:
 case([call(0x407710,args=[AFILES,0xabc,0xffffffff,ASSET,arg])],label='direct original asset completion callback argument gate')
# Two outstanding operations require both alternating batches. Diagnostic output
# releases the external producer's completion flag before each blocking wait.
for buffer in [0,1]:
 p,ch=completion_changes(buffer,1)
 other=buffer^1;ch[0x7cf184+4*other]=1;ch[0x7cf17c]=2
 for k,v in enumerate([AFILES,7,0x778899]):ch[0x7cefb8+other*192+k*4]=v
 p += [patch(AFILES+0x38,'<I',2),patch(CONTROL+4,'<I',0x7cf180)]
 case([call(0x5b6a50,args=[1])],p,ch,label='full wait repeats across two buffers until pending operations drain')
 assert oracle.word(CONTROL)==5
# Lookup waiting uses the actual ready/data methods. State 4 is supplied by an
# explicitly instrumented external scheduler; the asset parser is not recovered.
for buffer in [0,1]:
 p=[patch(ASSET+8,'<I',2),patch(CONTROL+4,'<3I',0x7cf180,ASSET+8,1)]
 case([call(0x407c00,AM,[0x123,1])],p,{0x7cf18c:buffer},label='not-ready lookup waits while external scheduler completes asset readiness')
 assert oracle.word(ASSET+8)==4 and oracle.word(CONTROL)==2
# First lookup waits; external producer changes the reader's key before the
# second lookup. This distinguishes the original double-lookup implementation.
p=[patch(ASSET+8,'<I',2),patch(AB+48,'<3I',0x124,ASSET2,0),patch(CONTROL+4,'<6I',0x7cf180,ASSET+8,1,READER+4,0x124,1)]
case([call(0x48cfd0,READER,[0x123])],p,label='two lookups re-read the key after external completion')
assert oracle.cases[-1]['steps'][0]['result']==BASE+0x1c1100

scope='Twenty-eight complete routines cover balance animation controller construction/all four commands, timeline setup, component access, reader pools/selection, asset table lookup and asynchronous callback pumping. Concrete asset ready/data/read-finished methods and the original registered file callback execute unchanged; callbacks reach state 2, not readiness 4. Diagnostic observers model an external completion producer/scheduler for blocking-wait tests; animation loading/parsing and real I/O integration remain unfinished. Required animation setup fields, valid buffers/pool indices/sentinels and successful controller allocation are internal contracts. Whole arena/globals/heap/returns compare; only arithmetic NaNs use classification and x87 bound stores explicitly quiet signaling NaNs. Channel command dispatch, full balance/movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'animation-assets-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_diagnostic_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':[[0x407710,'thug_asset_read_callback']],'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]}]}
path=out/'animation-assets-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'animation-asset-callbacks.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/animation_asset_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(diagnostics),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_assets_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'diagnostics':dict(diagnostics),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
