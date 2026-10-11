"""Compare complete animation-file loading and ownership with original x86."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_animation_cache.py').read_text().split('for low,high in')[0]
prefix=prefix.replace("'animation-cache.json'","'animation-loading.json'").replace('BASE,SIZE=0x1000000,0x100000','BASE,SIZE=0x1000000,0x200000').replace('0x18000,0x20000,0x40000','0x18000,0x40000,0x100000')
exec(compile(prefix,str(Path(__file__).with_name('verify_animation_cache.py')),'exec'))
from prx import entries
NEW=[
 (0x4819e0,'thug_animation_file_event_destroy',0,'void',False,True),
 (0x486460,'thug_animation_file_event_delete',1,'word',True,True),
 (0x486490,'thug_animation_transform_event_initialize',4,'word',False,True),
 (0x486680,'thug_animation_parse_file_event',1,'word',True,False),
 (0x482af0,'thug_keyframe_animation_initialize',0,'word',False,True),
 (0x482b30,'thug_keyframe_animation_destroy',0,'void',True,True),
 (0x484200,'thug_keyframe_animation_parse_compressed',1,'byte',True,True),
 (0x484370,'thug_keyframe_animation_parse_fixed',1,'byte',True,True),
 (0x4856c0,'thug_keyframe_animation_load_buffer',3,'byte',True,True),
 (0x4809f0,'thug_animation_cache_initialize',2,'void',True,True)]
for a,n,argc,result,heap,this in NEW:
 functions[hex(a)]={'name':n,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap}
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
for a in [0x420ac0,0x420140,0x4015d0,0x401cc0,0x5bbb60]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
FILE,EVENT,CURSOR,EVENT_ARRAY=BASE+0x90000,BASE+0x19000,BASE+0x19100,BASE+0x19200
exports=[[0x6487b0,'thug_animation_event_base_methods'],[0x648848,'thug_animation_file_transform_methods']]+[[0x64880c+i*12,'thug_animation_file_word_methods',i*12] for i in range(5)]
fields={b+0x20 for b in blocks}|{EVENT}
floats=set();quiet=set()
def identity(cpu,address,size,user):
 at=cpu.reg_read(UC_X86_REG_ECX);fields.add(at)
 if address==0x486490:
  floats.update(at+i for i in [12,16,20,24])
  position=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+12)
  # Overlapping position inputs can copy arithmetic NaNs from the just-written
  # quaternion; preserve that typed provenance through the sequential stores.
  for target,source in [(at+28,position),(at+32,position+8),(at+36,position+4)]:
   if source in floats:floats.add(target)
  if at+36 not in floats:quiet.add(at+36)
for a in [0x4819e0,0x486460,0x486490]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=a,end=a)
def parsed(cpu,address,size,user):
 at=cpu.reg_read(UC_X86_REG_EAX)
 if at:assert BASE<=at<BASE+SIZE;fields.add(at)
for a in [0x4866dd,0x48670c,0x48677b,0x4867eb,0x486812,0x48683d,0x486868]:oracle.cpu.hook_add(UC_HOOK_CODE,parsed,begin=a,end=a)
record=oracle.record
def relocated_record(kind,a,b,c):
 log=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48;ptr=a if kind==2 else c
 for i in range(4):
  if ptr+i*4 in fields:fields.add(log+16+i*4)
  if ptr+i*4 in floats:floats.add(log+16+i*4)
 record(kind,a,b,c)
oracle.record=relocated_record
def manager_blocks(cpu,address,size,user):
 # Once initialization returns, the 50 known block objects can register cleanup.
 m=cpu.reg_read(UC_X86_REG_ECX)
 # The next allocator result is the object whose callback field is at +0x20.
 fields.add(oracle.word(CONTEXT)+0x20)
oracle.cpu.hook_add(UC_HOOK_CODE,manager_blocks,begin=0x401cc0,end=0x401cc0)
asset_root=ROOT/'local/game-files/Game/Data'
archive=asset_root/'pre/Bits.prx';asset_hashes={str(archive.relative_to(ROOT)):hashlib.sha256(archive.read_bytes()).hexdigest()}
for entry in entries(archive.read_bytes()):
 key=entry.name.lower()
 if key in ['anims\\standardkeyq.bin','anims\\standardkeyt.bin']:
  assert not entry.compressed and len(entry.payload)==2048
  start=0x6f9ad8 if key.endswith('keyq.bin') else 0x6f92d8
  for i,value in enumerate(struct.unpack('<512I',entry.payload)):defaults[index[start+4*i]]=value
initial=bytes(memory);oracle.initial=initial
base_case=case
def case(calls,patches=(),changes=None,label='animation loading'):
 floats.clear();quiet.clear()
 stages=base_case(calls,patches,changes,label)
 for s in stages:
  s['float_fields']=sorted(floats);s['quiet_float_fields']=sorted(quiet)
 return stages
rng=random.Random(0x4856c0)
for i in range(64):
 case([call(0x482af0,ANIMATION)], [raw(ANIMATION,bytes(rng.getrandbits(8) for _ in range(60)))],label='initializer preserves flags key counts and upper reference bits')
for flag in [0,1,2,3,255,256,257,258,0xffffffff]:
 case([call(0x4819e0,EVENT),call(0x486460,EVENT,[flag])],[raw(EVENT,b'\xa5'*48)],label='event destruction and low-byte scalar delete')
special=[0,0x80000000,1,0x80000001,0x3f800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for i in range(160):
 rotation=[rng.choice(special) for _ in range(4)] if i>=64 else [struct.unpack('<I',struct.pack('<f',rng.uniform(-4,4)))[0] for _ in range(4)]
 position=[rng.choice(special) for _ in range(4)]
 q=[INPUT,EVENT+4,EVENT+8,EVENT+12,EVENT+16,EVENT+20][i%6]
 p=[INPUT+32,EVENT+4,EVENT+8,EVENT+12,EVENT+16,EVENT+20,EVENT+24,EVENT+28][i%8]
 case([call(0x486490,EVENT,[rng.getrandbits(32),q,p,rng.getrandbits(32)])],[raw(EVENT,b'\xa5'*64),patch(q,'<4I',*rotation),patch(p,'<4I',*position)],label='transform event finite and nonfinite components plus overlapping vectors')
def event(kind,frame=123,size=0xdeadbeef):
 payload=struct.pack('<8f',1,2,3,4,.25,.5,.75,1) if kind in [2,7] else bytes(range(32)) if kind==3 else struct.pack('<I',0xabcdef12)
 return struct.pack('<3I',frame&0xffffffff,kind,size&0xffffffff)+payload
for kind in [0,1,2,3,4,5,6,7,8,0xffffffff]:
 for size in [0,1,4,32,0xffffffff]:
  case([call(0x486680,args=[CURSOR])],[patch(CURSOR,'<I',INPUT),raw(INPUT,event(kind,0xffffffff,size))],label='all file event types and ignored or wrapping declared payload sizes')
for kind in range(1,8):
 for offset in [0,4,8,12,16,24,28,32,40]:
  case([call(0x486680,args=[INPUT+offset])],[raw(INPUT,event(kind)),patch(INPUT+offset,'<I',INPUT)],label='cursor pointer aliases header or payload words')
for align in [0,1,2,3,16,128,0xffffffff]:
 for fmt in [0,2,3,4,0xffffffff]:
  case([call(0x4809f0,MANAGER,[align,fmt])],[raw(MANAGER,b'\xa5'*0xe0)],label='manager initializes 50 allocated blocks and preserves unrelated fields')

def file_data(flags,bones=3,rc=5,tc=7,kinds=(),address=FILE,mask_count=50):
 data=bytearray(struct.pack('<7I',1,flags,0x3f800000,bones,rc&0xffffffff,tc&0xffffffff,len(kinds)))
 def align():data.extend(b'\xcc'*((-(address+len(data)))&3))
 def mask():
  n=(mask_count-1)&0xffffffff;n=n if n<0x80000000 else n-0x100000000
  size=8+4*(abs(n)//32*(-1 if n<0 else 1))
  assert size>=4;data.extend(struct.pack('<I',mask_count)+b'\x33'*(size-4))
 if not flags&0x10000000:
  data+=struct.pack('<2I',9,11)+b'\x11\0'*(bones*2);align()
  if flags&0x2000:data+=bytes(range(256))*6
  if flags&0x80000:mask()
  align()
  if not flags&0x9000000:data+=b'\x12'*9+b'\x34'*11
 else:
  if flags&0x1000000:data+=b'\x55'*(bones*4)
  if flags&0x80000:mask()
  data+=b'\x22'*(bones*(4 if flags&0x400000 else 2));align()
  stride=16 if flags&0x9000000 else 8
  data+=b'\x66'*(max(rc,0)*stride)+b'\x77'*(max(tc,0)*stride)
 align()
 for kind in kinds:data+=event(kind)
 return data
for fixed in [False,True]:
 for bits in range(32):
  flags=(0x10000000 if fixed else 0x800000)|sum(v for i,v in enumerate([0x2000,0x80000,0x1000000,0x8000000,0x400000]) if bits&(1<<i))
  address=FILE+(bits%4);kinds=[] if bits%4==0 else list(range(1,8)) if bits%4==1 else [1,7,8,2] if bits%4==2 else [8]
  data=file_data(flags,kinds=kinds,address=address,mask_count=[0,1,32,33,64][bits%5])
  root=0x484370 if fixed else 0x484200
  patches=[raw(address,data),raw(ANIMATION,b'\xa5'*60),patch(ANIMATION+4,'<I',flags),patch(ANIMATION+0x24,'<I',0),patch(ANIMATION+0x38,'<h',9)]
  calls=[call(root,ANIMATION,[address+12])]
  if 8 not in kinds:calls.append(call(0x482b30,ANIMATION))
  result=case(calls,patches,label='file parser flags alignment dictionaries masks and partial unknown event failure')
  assert result[0]['result']==int(8 not in kinds)
for rc,tc in [(-32768,32767),(-1,1),(32767,-32768),(0,0),(0x10000,0x10001)]:
 for flags in [0x10000000,0x11000000,0x18000000]:
  data=file_data(flags,rc=0,tc=0)
  struct.pack_into('<2I',data,16,rc&0xffffffff,tc&0xffffffff)
  case([call(0x484370,ANIMATION,[FILE+12])],[raw(FILE,data),patch(ANIMATION+4,'<I',flags)],label='fixed parser signed low-halfword key counts and pointer arithmetic')
for flags in [0,1,0x8000000,0x1000000]:
 case([call(0x4856c0,ANIMATION,[FILE,0,0xffffffff])],[raw(FILE,file_data(flags))],label='unsupported format returns false after copying duration and flags')
for count in [-32768,-1,0,1,7]:
 for manager in [0,MANAGER]:
  patches=[patch(ANIMATION+0x38,'<h',count),patch(ANIMATION+0x28,'<I',EVENT_ARRAY),patch(EVENT_ARRAY,'<7I',*[EVENT+i*64 if i%3 else 0 for i in range(7)]),patch(ANIMATION+0x24,'<I',BLOCKS)]
  for i in range(7):patches.append(patch(EVENT+i*64,'<I',0x64880c+(i%5)*12));fields.add(EVENT+i*64)
  case([call(0x482b30,ANIMATION)],patches,{0x6f92b0:manager},label='signed event count null slots and missing cache manager during destruction')

real_files=sorted(asset_root.rglob('*.ska.xbx'));builds=[]
for i,path in enumerate(real_files):
 data=path.read_bytes();asset_hashes[str(path.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
 version,flags=struct.unpack_from('<2I',data);assert version==1
 result=case([call(0x482af0,ANIMATION),call(0x4856c0,ANIMATION,[FILE,len(data),0]),call(0x482b30,ANIMATION)],[raw(FILE,data)],label='installed clip '+str(path.relative_to(asset_root)))
 assert result[1]['result']==1,(path,flags)
 if 'THPS6_skater_basics' in str(path) and not flags&0x19000000 and len(builds)<12:builds.append(path)
 if i%200==0:print('loaded real clips',i+1,'/',len(real_files),flush=True)
for path in builds:
 data=path.read_bytes()
 for fmt in [2,3,4]:
  # Exercise the implicit cache path as well as a complete initialized manager.
  modified=bytearray(data);struct.pack_into('<I',modified,4,struct.unpack_from('<I',modified,4)[0]|0x800)
  result=case([call(0x4809f0,MANAGER,[16,fmt]),call(0x482af0,ANIMATION),call(0x4856c0,ANIMATION,[FILE,0,0xffffffff]),call(0x482b30,ANIMATION)],[raw(FILE,modified)],label='real skater clip load precache and destruction format '+str(fmt)+' '+path.name)
  assert result[2]['result']==1

adapter=out/'animation-loading-memory.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/animation_cache_memory.c'),'-o',str(adapter)],check=True)
scope='Ten complete routines recover the two animation file layouts, all seven file-event constructors, event/keyframe ownership cleanup, buffer dispatch and initialization of 50 cache blocks. All 1,707 installed clips load and release through original x86 and recovered C; twelve skater clips additionally run the original decoder/cache builder in three formats using the exact two dictionaries from Bits.prx. Heap operations remain explicit host boundaries. All arena bytes, globals, returned values and heap records compare; only typed quaternion arithmetic NaNs use classification and signaling position NaNs require the physical x87 quiet bit. Unknown events preserve partial parse state. Parsers borrow trusted, bounded input; a production file-validation boundary and file-event action dispatch remain unfinished, as do rendering, controller integration and playable training.'
fixture={'base':BASE,'memory':'animation-loading-memory.bin','memory_adapter':ADAPTER,'memory_fixture':adapter.name,'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_animation_cache_scope','fixture_animation_cache_available'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'function_exports':[[0x482b90,'thug_keyframe_animation_cache_cleared']],'pointer_exports':exports,'pointer_fields':sorted(fields)}
path=out/'animation-loading-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),sum(oracle.counts.values()),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_loading_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'heap_service_events':dict(services),'scope':scope,'real_animation_files':len(real_files),'real_precache_builds':len(builds)*3,'input_hashes':asset_hashes,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()),'new roots',len(NEW))
