"""Original animation timing, controller cleanup and owned frame-event comparisons."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_animation_assets.py').read_text().split('rng=random.Random(0x4a4af0)')[0]
exec(compile(prefix.replace("'animation-assets.json'","'animation-events.json'"),str(Path(__file__).with_name('verify_animation_assets.py')),'exec'))
NEW=[
 (0x4015d0,'thug_allocate_array_storage',1,'word',True,False,False),
 (0x4645e0,'thug_animation_reader_free',1,'void',True,False,False),
 (0x48d000,'thug_animation_reader_delete',1,'word',True,False,True),
 (0x4b22a0,'thug_animation_reader_release',1,'void',True,False,False),
 (0x48bfd0,'thug_release_animation_reader',1,'void',True,False,False),
 (0x4814b0,'thug_animation_advance_time',0,'double',False,False,True),
 (0x4816b0,'thug_animation_offset_time',1,'void',False,False,True),
 (0x481830,'thug_animation_channel_initialize',1,'word',False,False,True),
 (0x481690,'thug_animation_timeline_destroy',0,'void',False,False,True),
 (0x4816e0,'thug_animation_timeline_delete',1,'word',True,False,True),
 (0x481a30,'thug_animation_insert_controller',2,'void',False,False,True),
 (0x481a80,'thug_animation_find_controller',1,'word',False,False,True),
 (0x4818b0,'thug_animation_remove_controller',1,'void',True,False,True),
 (0x4a4a80,'thug_balance_animation_destroy',0,'void',True,False,True),
 (0x4a50e0,'thug_balance_animation_delete',1,'word',True,False,True),
 (0x4a4610,'thug_animation_configure_controller',1,'void',False,False,True),
 (0x481a20,'thug_animation_event_initialize',0,'word',False,False,True),
 (0x486150,'thug_animation_event_set_enabled',1,'void',False,False,True),
 (0x4865d0,'thug_animation_event_setup',3,'void',True,False,True),
 (0x486560,'thug_animation_event_destroy',0,'void',True,False,True),
 (0x481db0,'thug_animation_event_delete',1,'word',True,False,True),
 (0x4819f0,'thug_animation_event_base_delete',1,'word',True,False,True),
 (0x4860c0,'thug_animation_event_crosses',3,'word',False,False,True),
 (0x486160,'thug_animation_event_trigger',1,'byte',True,True,True),
 (0x486440,'thug_animation_event_emit',1,'byte',True,True,True),
 (0x481bb0,'thug_animation_clear_events',0,'void',True,False,True),
 (0x481c00,'thug_animation_load_events',1,'void',True,False,True),
 (0x4819a0,'thug_animation_reset_events',0,'void',False,False,True),
 (0x481e10,'thug_animation_update_events',2,'void',True,True,True)]
assert len(NEW)==29
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
for at,args_ in [(0x4816b0,[0]),(0x4860c0,[0,1]),(0x481e10,[0,1])]:functions[hex(at)]['float_args']=args_
for at in [0x4609f0,0x462f00,0x460470,0x473800,0x478540,0x62388b,0x62382b,0x5ba400]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
EV,EV2,CTLS,LINKS,OTHERPOOL,OTHERBLOCKS=[BASE+x for x in [0x1c9004,0x1ca004,0x1cb000,0x1cc000,0x1cd000,0x1cd100]]
memory[EV-4-BASE:OTHERBLOCKS+0x1000-BASE]=bytes(OTHERBLOCKS+0x1000-(EV-4))
put(EV-4,'<I',8);put(EV2-4,'<I',8)
for at in [EV,EV2]:
 for i in range(8):put(at+i*20,'<IiB3xII',0x6487bc,i*10,1,0xabc100+i,0);fields.add(at+i*20)
for i in range(7):
 at=CTLS+i*0x40;put(at,'<5I',0x649f80,CHANNEL,0,i,0xabc000+i);fields.add(at)
put(CHANNEL+0x68,'<2I',EV,8);put(CHANNEL+0x70,'<B',1);put(CHANNEL+0x38,'<I',2)
put(OTHERPOOL,'<6I',OTHERBLOCKS,OTHERBLOCKS+0x900,0,0,0,OTHERBLOCKS)
for i in range(4):put(OTHERBLOCKS+i*0x220,'<I',OTHERBLOCKS+(i+1)*0x220 if i<3 else 0)
exports += [[0x6486cc,'thug_animation_link_methods'],[0x648794,'thug_animation_channel_methods'],[0x6487b0,'thug_animation_event_base_methods'],[0x6487bc,'thug_animation_event_methods']]
for at in [0x481830,0x481690,0x4a4a80,0x481a20,0x486560,0x48d000]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
if 0x684fc8 not in index:addglobal('thug_frame_length_scale',0x684fc8,0x3f800000)
else:defaults[index[0x684fc8]]=0x3f800000
# Real registered objects receive each event through 461140 and their QB table.
# Only the terminal native command is an instrumented test observer.
EVENT_STATE,PROGRAM,NATIVE=BASE+0x1cf000,BASE+0x1ce000,oracle.stop+0x400
memory[EVENT_STATE-BASE:EVENT_STATE-BASE+4096]=bytes(4096)
put(EM+0x14,'<I',0)
put(PRIMARY+8,'<I',2)
for i,widget in enumerate([WIDGET,NUMERIC]):
 put(PRIMARY+32+i*12,'<3I',0x100+i,widget,0)
 put(widget+0x14,'<I',0x100+i);put(widget+0x10,'<I',SCRIPTS)
script=bytearray(244)
for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
memory[SCRIPTS-BASE:SCRIPTS-BASE+244]=script
put(EVENTS,'<IIBBHI',ENTRIES,8,1,0,0,0)
for i in range(8):put(ENTRIES+i*20,'<5I',0xabc100+i,NOTIFY,0,0,1)
memory[PROGRAM-BASE:PROGRAM-BASE+8]=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24'
# Objective prefix installs NOTIFY's current symbol/cache pair at META.
put(META+12,'<I',PROGRAM);put(META+36,'<I',PROGRAM)
fields.update([SCRIPTS+0xec,PROGRAM+2])
def event_native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
 n=oracle.word(EVENT_STATE);assert n<32;oracle.setword(EVENT_STATE,n+1)
 row=[oracle.word(CHANNEL+0x6c),oracle.word(CHANNEL+0x64),oracle.word(CHANNEL+0x68),oracle.word(script+0xc8),oracle.word(script+0xbc),oracle.word(params+4) if params else 0]
 row += [bytes(cpu.mem_read(EV+i*20+8,1))[0] for i in range(8)]
 cpu.mem_write(EVENT_STATE+128+n*64,struct.pack('<16I',*row,0,0))
 if n==0:
  for off in [4,16,28]:
   at=oracle.word(EVENT_STATE+off);value=oracle.word(EVENT_STATE+off+4);width=oracle.word(EVENT_STATE+off+8)
   if at:assert width in [1,4];cpu.mem_write(at,value.to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,event_native,begin=NATIVE,end=NATIVE)
initial=bytes(memory);oracle.initial=initial
base_case=old_case
def case(calls,patches=(),changes=None,label='animation events'):
 stages=base_case(calls,patches,changes,label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=EVENT_STATE and at+len(data)//2>=EVENT_STATE+4:
    current=int.from_bytes(bytes.fromhex(data)[EVENT_STATE-at:EVENT_STATE-at+4],'little');s['callbacks']=current-previous;previous=current
  if s['fn']=='0x4816b0':s['float_fields']=[CHANNEL+0x18]
 return stages
rng=random.Random(0x481e10)
for i in range(12):
 p=[raw(CHANNEL,bytes(rng.getrandbits(8) for _ in range(0x74))),raw(EV,bytes(rng.getrandbits(8) for _ in range(20)))]
 case([call(0x481830,CHANNEL,[BODIES]),call(0x481a20,EV)],p,label='constructors preserve all unwritten bytes')
for size in [0,1,4,20,164,4096]:case([call(0x4015d0,args=[size])],label='array allocation preserves allocator fill')
for val in [0,1,2,255,256,257,0xffffff00,0xffffffff]:case([call(0x486150,EV,[val])],label='enabled coerces low byte only')
# Full signed frames, equal and reversed boundaries, endpoints and NaNs.
special=[0,0x80000000,1,0x80000001,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for frame in [-2147483648,-16777217,-1,0,1,16777217,2147483647]:
 ends=[bits(float(frame)),bits(float(frame)-256),bits(float(frame)+256)]+special
 for a,z in [(a,z) for a in ends[:3] for z in ends[:3]]+[(a,rng.choice(ends)) for a in ends[3:]]:
  for inclusive in [0,1,256,257]:case([call(0x4860c0,EV,[a,z,inclusive])],[patch(EV+4,'<i',frame)],label='signed frames and precise directional crossing boundaries')
# Finite, ordered ranges ensure the original wrap loops terminate.
for i in range(320):
 start=rng.uniform(-50,0);end=rng.uniform(1,80);current=rng.choice([start,end,rng.uniform(start-100,end+100)])
 speed=rng.uniform(-4,4);direction=rng.choice([0,0xffffffff,1,2]);loop=i%6
 p=[patch(CHANNEL+0x14,'<4f',start,current,end,speed),patch(CHANNEL+0x24,'<2I',direction,loop),patch(CHANNEL+0x2c,'<B',255)]
 case([call(0x4814b0,CHANNEL),call(0x4816b0,CHANNEL,[bits(rng.uniform(-100,100))])],p,{0x684fc8:bits(rng.choice([0,.5,1,2,20]))},label='timing clamp wrap reversal offset and invalid direction')
for loop in [0,1,2,3,4]:
 for direction in [0,0xffffffff]:
  for current in [-1,0,1]:
   case([call(0x4814b0,CHANNEL),call(0x4816b0,CHANNEL,[bits(1)])],[patch(CHANNEL+0x14,'<4f',0,current,0,2),patch(CHANNEL+0x24,'<2I',direction,loop)],label='zero-width timeline terminates')
for value in special:
 case([call(0x4814b0,CHANNEL),call(0x4816b0,CHANNEL,[value])],[patch(CHANNEL+0x14,'<4I',value,value,value,value),patch(CHANNEL+0x28,'<I',3)],label='disabled timeline returns zero before arithmetic')
# Equal or unordered bounds avoid unbounded wrapping with extreme inputs.
for value in special:
 for direction in [0,0xffffffff,1]:
  for loop in [0,1,2]:
   case([call(0x4814b0,CHANNEL)],[patch(CHANNEL+0x14,'<4I',value,value,value,0),patch(CHANNEL+0x24,'<2I',direction,loop)],label='nonfinite equal or unordered bounds and wider x87 return')
# Unlink a real list, including self-links and neighbouring nodes.
for shape in [0,1,2]:
 p=[patch(CHANNEL+12,'<2I',CHANNEL if shape==0 else LINKS,CHANNEL if shape==0 else LINKS+(0x80 if shape==2 else 0))]
 for i in range(2):p.append(patch(LINKS+i*0x80+12,'<2I',CHANNEL,CHANNEL))
 for flag in [0,1,2,256,257]:case([call(0x4816e0,CHANNEL,[flag])],p,label='timeline delete and linked neighbour rewrites')
case([call(0x481650,CHANNEL),call(0x481690,CHANNEL)],label='standalone timeline unlink')
for count in [0,1,3,5]:
 for priority in [-2147483648,-1,0,1,4,2147483647]:
  p=[patch(CHANNEL+0x3c,'<6I',*[CTLS+i*0x40 for i in range(6)]),patch(CHANNEL+0x54,'<i',count)]
  for i in range(6):p.append(patch(CTLS+i*0x40+12,'<i',[4,1,1,0,-1,-2147483648][i]))
  case([call(0x481a30,CHANNEL,[CTLS+6*0x40,priority]),call(0x481a80,CHANNEL,[0xabc006]),call(0x481a80,CHANNEL,[0xabc001]),call(0x481a80,CHANNEL,[0x123]),call(0x4818b0,CHANNEL,[CTLS+6*0x40])],p,label='stable signed-priority insertion lookup and actual controller delete')
for count in [-1,0,1,3,6]:
 for victim in [0,CTLS,CTLS+64,CTLS+5*64,CTLS+6*64]:
  p=[patch(CHANNEL+0x54,'<i',count),patch(CHANNEL+0x3c,'<6I',*[0 if i==2 else CTLS+i*64 for i in range(6)])]
  case([call(0x4818b0,CHANNEL,[victim])],p,label='remove missing null first middle and last controller; stale tail slot')
for value in [None,0,1,0xffffffff]:
 b=Build();params=b.structure([] if value is None else [(0x40c698af,13,value)])
 case([call(0x4a4610,CONTROLLER,[params])],b.patches(),label='shared forwarding configure method')
# Heap, selected pool, alternate pool and out-of-pool reader cleanup.
for pool_index in [0,1]:
 for where in ['heap','selected','alternate','outside']:
  reader=READER if where in ['heap','outside'] else (ABLOCKS if where=='selected' else OTHERBLOCKS)+0x220
  changes={0x6fa7f4:pool_index,0x6fa7fc+pool_index*4:APOOL if where!='heap' else 0,0x6fa7fc+(pool_index^1)*4:OTHERPOOL if where!='heap' else 0}
  p=[patch(reader,'<I',0x648a68),patch(CONTROLLER+0x2c,'<I',reader)];fields.add(reader)
  for flag in [0,1,2,256,257]:case([call(0x48d000,reader,[flag])],p,changes,label='reader scalar delete '+where)
  for root in [0x4645e0,0x4b22a0,0x48bfd0]:case([call(root,args=[reader])],p,changes,label='reader cleanup wrapper '+where)
  for root in [0x4a4a80,0x4a50e0]:case([call(root,CONTROLLER,[1] if root==0x4a50e0 else [])],p,changes,label='full balance-controller cleanup '+where)
for root in [0x4b22a0,0x48bfd0]:case([call(root,args=[0])],label='null generic delete wrapper')
for animation in [0,0x12345678]:case([call(0x4a4a80,CONTROLLER)],[patch(CONTROLLER+0x2c,'<2I',0,animation)],label='controller destroy without reader')
# Owned parameters, nested values and reverse array destruction.
for i in range(20):
 b=Build();nested=b.structure([(1,3,b.text(b'owned event payload')),(2,12,b.array(1,[1,2,3]))])
 params=b.structure([(0x111,1,i),(0x222,10,nested),(0x333,2,0x7f812345)]) if i%3 else 0
 calls=[call(0x481a20,EV),call(0x4865d0,EV,[i-10,0xabc100+i,params])]
 if i%4==0:calls+=[call(0x486560,EV)]
 else:calls+=[call(0x481db0,EV,[i%2])]
 case(calls,b.patches(),label='setup deep copies and destroys nested owned event parameters')
for count in [0,1,4,8]:
 for flag in [2,3,258,259]:
  b=Build();p=b.structure([(1,3,b.text(b'reverse release order'))]);calls=[]
  for i in range(count):calls.append(call(0x4865d0,EV+i*20,[i,0xabc100+i,p]))
  calls.append(call(0x481db0,EV,[flag]))
  case(calls,b.patches()+[patch(EV-4,'<I',count)],label='vector delete destroys backwards and releases header')
for flag in [0,1,2,3,256,257]:case([call(0x4819f0,EV,[flag])],label='base scalar delete only tests low bit')
for count in [0,1,8]:
 for pointer in [0,EV]:
  for header in [0,1,8]:
   case([call(0x481bb0,CHANNEL)],[patch(CHANNEL+0x68,'<2I',pointer,count),patch(EV-4,'<I',header)],label='clear gate count pointer and allocated header count')
for count in [0,1,8]:
 p=[patch(CHANNEL+0x6c,'<I',count)]+[patch(EV+i*20+8,'<B',rng.randrange(256)) for i in range(8)]
 case([call(0x4819a0,CHANNEL)],p,label='reset enabled bytes only')
# Event tables from real QB arrays. Existing storage is deliberately not cleared
# on missing/empty definitions, matching the caller-owned lifetime protocol.
EVENT_KEY=0xabc55
for missing in ['component','sentinel','zero-name','symbol','array','empty']:
 b=Build();extra=[]
 if missing=='component':extra.append(patch(BODIES+0x100,'<I',0))
 elif missing=='sentinel':extra.append(patch(ASTATE+4,'<I',0xffffffff))
 elif missing=='zero-name':extra.append(patch(ASTATE+0x58,'<I',0))
 elif missing in ['array','empty']:b.symbol(0xabc123,10,b.structure([] if missing=='array' else [(EVENT_KEY,12,b.array(10,[]))]))
 case([call(0x481c00,CHANNEL,[EVENT_KEY])],b.patches()+extra,label='load event early return '+missing)
for count in [1,2,8]:
 for seconds in [False,True]:
  b=Build();entries=[]
  for i in range(count):
   params=b.structure([(0x111,3,b.text(b'animation')),(0x222,10,b.structure([(3,1,i)]))])
   frame=(0x906b67ba,2,bits((i-2)*.125)) if seconds else (0x4a07c332,1,(i-2)&0xffffffff)
   entries.append(b.structure([frame,(0xc451f558,13,0xabc100+i)]+([(0x7031f10c,10,params)] if i%2 else [])))
  b.symbol(0xabc123,10,b.structure([(EVENT_KEY,12,b.array(10,entries))]))
  case([call(0x481bb0,CHANNEL),call(0x481c00,CHANNEL,[EVENT_KEY]),call(0x4819a0,CHANNEL),call(0x481bb0,CHANNEL)],b.patches(),label='load QB event array integer/seconds with nested parameter ownership')
# Delivery cases are extended below with actual object routing and QB handlers.
for enabled in [0,1,2,255]:
 case([call(0x486160,EV,[BODIES]),call(0x486160,EV,[BODIES]),call(0x486440,EV,[BODIES])],[patch(EV+8,'<B',enabled)],label='one-shot trigger and explicit emission through real event manager')
for direction in [0,0xffffffff,1]:
 for a,z in [(0,1),(1,0),(.5,.5),(.25,.75),(10,-10)]:
  case([call(0x481e10,CHANNEL,[bits(a),bits(z)])],[patch(CHANNEL+0x24,'<I',direction)],label='event updates crossing wrap reset and exclusive final endpoint')
for enabled,mode in [(0,2),(1,0),(1,1),(1,3),(255,0xffffffff)]:case([call(0x481e10,CHANNEL,[0,bits(1)])],[patch(CHANNEL+0x70,'<B',enabled),patch(CHANNEL+0x38,'<I',mode),patch(CHANNEL+0x68,'<I',0xffffffff)],label='event update gates before pointer access')

for a,z in [(a,z) for a in special for z in [0,bits(1),0x7f7fffff]]:
 case([call(0x481e10,CHANNEL,[a,z])],label='frame conversion nonfinite and overflow without early clamping')
for value in [0,0x80000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
 b=Build();entry=b.structure([(0x906b67ba,2,value),(0xc451f558,13,0xabc100)])
 b.symbol(0xabc123,10,b.structure([(EVENT_KEY,12,b.array(10,[entry]))]))
 case([call(0x481bb0,CHANNEL),call(0x481c00,CHANNEL,[EVENT_KEY]),call(0x481bb0,CHANNEL)],b.patches()+[patch(CONTEXT+24,'<I',CHANNEL+0x6c)],label='seconds conversion range and clear count before heap release')
# Mutation within the first real QB handler affects the remaining live loop.
for mutations in [
 [(CHANNEL+0x6c,0,4)],[(CHANNEL+0x6c,3,4)],[(CHANNEL+0x6c,8,4)],
 [(CHANNEL+0x68,EV2,4)],[(CHANNEL+0x64,BODIES+0x400,4)],
 [(EV+8,1,1)],[(EV+20+8,0,1)],[(EV+24,100,4)],
 [(CHANNEL+0x70,0,1)],[(CHANNEL+0x38,0,4)],
 [(CHANNEL+0x68,EV2,4),(CHANNEL+0x6c,3,4),(CHANNEL+0x64,BODIES+0x400,4)]]:
 p=[patch(CHANNEL+0x6c,'<I',6)]
 for i,(at,value,width) in enumerate(mutations):p.append(patch(EVENT_STATE+4+i*12,'<3I',at,value,width))
 case([call(0x481e10,CHANNEL,[0,bits(1)])],p,label='QB native callback mutates live array count owner or enabled bytes')
 assert oracle.word(EVENT_STATE)>0
# A disabled trigger must not touch an invalid owner; re-enabling in a handler
# survives the trigger and allows a second delivery.
case([call(0x486160,EV,[0xffffffff])],[patch(EV+8,'<B',0)],label='disabled trigger returns before owner dereference')
case([call(0x486160,EV,[BODIES])]*2,[patch(EVENT_STATE+4,'<3I',EV+8,1,1)],label='handler re-enables current event for a second trigger')
assert oracle.word(EVENT_STATE)==2

scope='Twenty-nine complete animation routines: timeline progression/offset, channel construction and unlink, ordered controller insertion/lookup/removal, balance-controller and reader cleanup, array allocation and owned frame-event setup/loading/cleanup/crossing/dispatch. Original gameplay callees and concrete virtual methods execute unchanged. Actual object routing and cached QB execute a terminal instrumented native observer; handlers mutate live arrays, counts, owner and enabled bytes. Tests compare all arena/global/heap/return bytes; arithmetic NaNs use classification only. Valid finite wrapping ranges, terminating scripts, initialized heap and successful allocation are contracts. Exception unwinding, channel command dispatch, animation parsing/rendering, complete movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'animation-events-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_native_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]},{'module':'animation-events-callbacks.wasm','export':'fixture_animation_event_native','original':NATIVE}]}
path=out/'animation-events-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
adapter=out/'animation-events-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/animation_events_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_events_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
