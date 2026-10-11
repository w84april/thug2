"""Compare keyframe decoding, cache ownership and complete cache builds with x86."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle

out=ROOT/'local/validation/collision';report_path=out.parent/'animation-cache.json'
report_path.unlink(missing_ok=True)
BASE,SIZE=0x1000000,0x100000
ADAPTER,CONTEXT,ALLOCATOR,MANAGER,BLOCKS,ANIMATION,INPUT,OUTPUT,TABLE,POOL,POOL_BLOCKS,ALT_POOL,ALT_BLOCKS,READER,KEYS,LENGTHS,LOG,HEAP=[BASE+x for x in [0x100,0x200,0x400,0x1000,0x2000,0x8000,0x9000,0xa000,0xb000,0xc000,0xc100,0xf000,0xf100,0x12000,0x15000,0x18000,0x20000,0x40000]]
CACHE_HEAP=ALLOCATOR+0x200
memory=bytearray(SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(ADAPTER,'<5I',CONTEXT,0,0,0,0)
put(CONTEXT,'<10I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0,0x20000,CACHE_HEAP)
blocks=[BLOCKS+i*0x180 for i in range(50)]
put(MANAGER,'<50I',*blocks);put(MANAGER+0xd0,'<2I',16,2)
for b in blocks:put(b+0x164,'<H',0x8000)
for pool,storage in [(POOL,POOL_BLOCKS),(ALT_POOL,ALT_BLOCKS)]:
 put(pool,'<6I',storage,storage+18*0x1e4,0,0,0,storage)
 for i in range(18):put(storage+i*0x1e4,'<I',storage+(i+1)*0x1e4 if i<17 else 0)
put(ANIMATION+8,'<I',1);put(ANIMATION+0x10,'<2I',KEYS,KEYS+0x1000)
put(ANIMATION+0x2c,'<2I',LENGTHS,LENGTHS+0x100);put(ANIMATION+0x34,'<2h',1,1)
NEW=[
 (0x5be8e0,'thug_animation_tick',0,'wide',False,False),
 (0x482c20,'thug_animation_decode_rotation',4,'word',False,False),
 (0x482e70,'thug_animation_decode_translation',3,'word',False,False),
 (0x482a70,'thug_animation_expand_rotation',2,'void',False,False),
 (0x483d00,'thug_animation_expand_quaternion',2,'void',False,False),
 (0x480660,'thug_animation_cache_instance',0,'word',False,False),
 (0x480800,'thug_animation_cache_format',0,'word',False,True),
 (0x4805e0,'thug_animation_cache_rotation_stride',0,'byte',False,True),
 (0x4805f0,'thug_animation_cache_translation_stride',0,'byte',False,True),
 (0x480600,'thug_animation_cache_rotations',1,'word',False,True),
 (0x480610,'thug_animation_cache_translations',1,'word',False,True),
 (0x480620,'thug_animation_cache_rotation_offsets',0,'word',False,True),
 (0x480630,'thug_animation_cache_translation_offsets',0,'word',False,True),
 (0x480640,'thug_animation_cache_set_cleanup',2,'void',False,True),
 (0x480670,'thug_animation_cache_allocation_size',4,'word',False,True),
 (0x480a70,'thug_animation_cache_reader_free',1,'void',True,False),
 (0x480ad0,'thug_animation_cache_clear',0,'word',True,True),
 (0x480bf0,'thug_animation_cache_pin_block',0,'word',True,True),
 (0x480c90,'thug_animation_cache_unpin_block',1,'void',True,True),
 (0x480df0,'thug_animation_cache_remove',1,'void',True,True),
 (0x480db0,'thug_animation_cache_flush',1,'void',True,True),
 (0x480e30,'thug_animation_cache_pin',1,'word',True,True),
 (0x480e80,'thug_animation_cache_unpin',2,'void',True,True),
 (0x480940,'thug_animation_cache_available',0,'word',True,True),
 (0x480810,'thug_animation_cache_allocate',5,'word',True,True),
 (0x480980,'thug_animation_cache_add',5,'word',True,True),
 (0x4806c0,'thug_animation_cache_oldest',2,'word',False,True),
 (0x480ed0,'thug_animation_cache_evict',2,'byte',True,True),
 (0x482ba0,'thug_keyframe_animation_pin',0,'word',True,True),
 (0x482bd0,'thug_keyframe_animation_unpin',1,'void',True,True),
 (0x482b90,'thug_keyframe_animation_cache_cleared',1,'void',False,False),
 (0x485270,'thug_keyframe_animation_build_cache',1,'void',True,True)]
functions={hex(a):{'name':n,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap} for a,n,argc,result,heap,this in NEW}
functions['0x480640']['pointer_args']=[0]
globals_=[];defaults=[];index={}
def addglobal(name,at,value=0,width=4,offset=0):
 assert at not in index
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
addglobal('thug_animation_cache_manager',0x6f92b0,MANAGER)
addglobal('thug_animation_cache_pool_index',0x6f92b8)
for i in range(2):addglobal('thug_animation_cache_pools',0x6f92c0+i*4,offset=i*4)
for name,at in [('thug_animation_tick_counter',0x7d1ed0),('thug_animation_cache_tick',0x6fa2e0)]:
 for i in range(2):addglobal(name,at+i*4,offset=i*4)
addglobal('thug_animation_cache_build_count',0x6fa2d8)
addglobal('thug_frame_counter',0x7d1ec8,100)
addglobal('thug_frame_rate',0x684fd0,0x42700000)
rng=random.Random(0x485270)
for name,at in [('thug_animation_rotation_table',0x6f9ad8),('thug_animation_translation_table',0x6f92d8)]:
 for i in range(512):addglobal(name,at+4*i,rng.getrandbits(32),offset=i*4)
initial=bytes(memory)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=[a for a,*_ in NEW]+[0x5ba3b0,0x5ba3d0,0x5ba400,0x5be970],event_limit=(HEAP-LOG)//48,instruction_limit=1000000,scope_entries={CACHE_HEAP:7})
services=Counter()
def heap_services(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==0x5baf50:
  assert oracle.word(sp+4)==0x8f21a798 and oracle.word(sp+8)==1
  result=CACHE_HEAP;cleanup=8;oracle.record(5,0x8f21a798,1,result)
 else:
  assert oracle.word(CONTEXT+28)==7
  result=oracle.word(CONTEXT+32);cleanup=0;oracle.record(4,result,0,0)
 services[hex(address)]+=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x5baf50,0x5bb050]:oracle.cpu.hook_add(UC_HOOK_CODE,heap_services,begin=at,end=at)
def initialize_padding(cpu,address,size,user):
 # The original copies two uninitialized stack-padding bytes in expanded
 # records. Seed only those bytes to zero; the port defines the same padding.
 sp=cpu.reg_read(UC_X86_REG_ESP)
 for delta in [-0x22,-0x12,-0x32]:cpu.mem_write(sp+delta,b'\0\0')
oracle.cpu.hook_add(UC_HOOK_CODE,initialize_padding,begin=0x485270,end=0x485270)
labels=[]
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]
def case(calls,patches=(),changes=None,label='animation cache'):
 result=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label);return result

for low,high in [(0,0),(0xffffffff,0),(0,1),(0xffffffff,0xffffffff),(0xdeadbeef,0x87654321)]:
 case([call(0x5be8e0)],changes={0x7d1ed0:low,0x7d1ed4:high},label='full 64-bit animation tick')
# Every packed rotation selector with all five controlling asset flags.
for bits in range(32):
 flags=sum(v for i,v in enumerate([0x100,0x2000,0x8000,0x10000,0x23]) if bits&(1<<i))
 for header_bits in range(16):
  header=(header_bits<<11)|(0x8000 if bits&1 else 0)|rng.randrange(0x800)
  data=struct.pack('<HH',rng.getrandbits(16),header) if flags&0x100 else struct.pack('<H',header)
  data+=bytes(rng.randrange(256) for _ in range(32))
  target=rng.choice([OUTPUT,INPUT,INPUT+1,INPUT+2,INPUT+4,INPUT+8,TABLE+6])
  case([call(0x482c20,args=[INPUT,target,flags,TABLE])],[raw(INPUT,data),raw(TABLE,bytes(rng.randrange(256) for _ in range(1536)))],label='packed rotation selectors and overlapping buffers')
for header in range(256):
 data=bytes([header])+bytes(rng.randrange(256) for _ in range(20));target=rng.choice([OUTPUT,INPUT,INPUT+1,INPUT+2,INPUT+4,INPUT+8])
 case([call(0x482e70,args=[INPUT,target,rng.getrandbits(32)])],[raw(INPUT,data)],label='all translation headers and overlap')
for target in [TABLE-2,TABLE,TABLE+1,TABLE+2,TABLE+4,TABLE+6]:
 case([call(0x482c20,args=[INPUT,target,0x2000,TABLE])],[raw(INPUT,b'\x00\x40\x00'),raw(TABLE,bytes(range(32)))],label='custom dictionary output overlap preserves sequential halfword loads')
for i in range(320):
 values=[0,0,0] if i<16 else [rng.choice([-32768,-16384,-1,0,1,16384,32767]) if i<160 else rng.randrange(-32768,32768) for _ in range(3)]
 data=struct.pack('<H3h',rng.getrandbits(16),*values)+bytes(rng.randrange(256) for _ in range(32))
 target=[OUTPUT,INPUT,INPUT+1,INPUT+2,INPUT+4,INPUT+6,INPUT-2,INPUT-4][i%8]
 case([call(0x482a70,args=[target,INPUT])],[raw(INPUT,data),raw(OUTPUT,b'\xa5'*32)],label='expanded rotation signed components and overlap')
 case([call(0x483d00,args=[target,INPUT])],[raw(INPUT,data),raw(OUTPUT,b'\xa5'*32)],label='expanded quaternion clamping sign and overlap')
for i in range(24):
 b=blocks[i%50];p=[patch(b+0x18,'<2I',rng.getrandbits(32),rng.getrandbits(32)),patch(b+0x70,'<2B',rng.randrange(256),rng.randrange(256)),patch(MANAGER+0xd4,'<I',rng.getrandbits(32))]
 case([call(0x480660),call(0x480800,MANAGER)]+[call(at,b,[0xdeadbeef] if at in [0x480600,0x480610] else []) for at in [0x4805e0,0x4805f0,0x480600,0x480610,0x480620,0x480630]]+[call(0x480640,b,[0x482b90,ANIMATION]),call(0x482b90,args=[ANIMATION]),call(0x482b90,args=[0])],p,label='accessors and registered cleanup')
for i in range(160):
 alignment=rng.choice([1,2,3,4,16,128,65535,0xffffffff]);fmt=rng.choice([0,1,2,3,4,5,0xffffffff])
 case([call(0x480670,MANAGER,[rng.getrandbits(32),rng.getrandbits(32),rng.getrandbits(32),fmt])],[patch(MANAGER+0xd0,'<I',alignment)],label='allocation sizing wraps before unsigned alignment')

def pooled(selected=0,which=0):return {0x6f92b8:selected,0x6f92c0+which*4:POOL}
for selected in [0,1]:
 for mode in ['heap','selected','alternate']:
  changes=pooled(selected,selected if mode=='selected' else selected^1) if mode!='heap' else {0x6f92b8:selected}
  ptr=READER if mode=='heap' else POOL_BLOCKS
  case([call(0x480a70,args=[ptr])],[raw(ptr,b'\xa5'*0x1e4)],changes,label='reader free '+mode)
 for first_free in [0,1,9,17,18]:
  for use_pool in [False,True]:
   p=[patch(BLOCKS+0x28,'<18I',*[READER if i<first_free else 0 for i in range(18)])]
   changes=pooled(selected,selected) if use_pool else {0x6f92b8:selected}
   case([call(0x480bf0,BLOCKS)],p,changes,label='first free reader and exhaustion')
for count in [0,1,2,8191]:
 for reader_index in [0,1,17]:
  for upper in [0,0x2000,0x8000,0xe000]:
   p=[patch(BLOCKS+0x164,'<H',upper|count),patch(BLOCKS+0x28+reader_index*4,'<I',READER),raw(READER,b'\xa5'*0x1e4)]
   case([call(0x480c90,BLOCKS,[reader_index])],p,label='unpin preserves reader zero and flag bits')

def active_block(b,asset=ANIMATION,refs=1,timestamp=10,size=64,storage=READER+0x800):
 return [patch(b,'<6I',asset,timestamp,2,storage,size,48),patch(b+0x18,'<4I',storage,storage+32,0x482b90,asset),patch(b+0x164,'<H',refs),patch(asset+0x24,'<I',b)]
for i in range(40):
 refs=rng.choice([0,1,2,8191,0x8000,0xa001]);p=active_block(BLOCKS,refs=refs)
 if i&1:p+=[patch(BLOCKS+0x28,'<18I',*[READER+j*0x200 if j%3==0 else 0 for j in range(18)])]
 p += [patch(MANAGER+0xc8,'<2I',1,64)]
 case([call(0x480ad0,BLOCKS),call(0x480ad0,BLOCKS)],p,label='block clear callback storage reader ownership')
for available in [0,15,16,63,64,65,0x20000,0xffffffff]:
 case([call(0x480940,MANAGER)],[patch(CONTEXT+32,'<I',available)],label='selected heap availability')
 for fmt in [0,2,3,4,5]:
  case([call(0x480810,BLOCKS,[ANIMATION,0x10003,2,1,fmt])],[patch(CONTEXT+32,'<I',available),patch(BLOCKS+0x164,'<H',0x6123)],label='allocation success and preserved failure fields')
for free_index in [0,1,25,49,50]:
 for duplicate in [-1,0,25,49]:
  p=[]
  for i,b in enumerate(blocks):p+=[patch(b,'<I',ANIMATION if i==duplicate else ANIMATION+0x100+i*4),patch(b+8,'<I',0 if i>=free_index else 2)]
  case([call(0x480980,MANAGER,[ANIMATION,3,2,1,3])],p,label='cache add first free versus duplicate ordering')
for i in range(64):
 p=[patch(OUTPUT,'<I',0x12345678),patch(MANAGER+0xc8,'<2I',50,3200)]
 for j,b in enumerate(blocks):
  p+=active_block(b,ANIMATION+(j%4)*0x40,refs=rng.choice([0,1,10,999,8191,0x2000,0xa003]),timestamp=rng.choice([0,5,10,100,1666,1667,0xffffffff]),size=rng.choice([0,16,64,128]),storage=0)
 minimum=rng.choice([0,16,64,129]);priority=rng.choice([0,1,10,1000,0xffffffff])
 case([call(0x4806c0,MANAGER,[minimum,OUTPUT]),call(0x480ed0,MANAGER,[priority,minimum])],p,label='oldest timestamp eligibility ties priority and multi-slot eviction')
for mask in range(8):
 for only in [0,1,256,257]:
  p=[patch(MANAGER+0xc8,'<2I',3,192)]
  for i in range(3):p+=active_block(blocks[i],ANIMATION+i*0x40,refs=(mask>>i)&1,storage=0)
  case([call(0x480db0,MANAGER,[only])],p,label='flush low-byte flag and retained manager count')
for ref in [0,1,2,3,0xfe,0x100,0x1fe,0x1ff,0x8000,0x8102,0xffff]:
 for evict in [0,1]:
  p=active_block(BLOCKS,refs=0,storage=0)+[patch(MANAGER+0xdc,'<B',evict),patch(MANAGER+0xc8,'<2I',1,64),patch(ANIMATION+0x3a,'<H',ref)]
  case([call(0x482ba0,ANIMATION),call(0x482bd0,ANIMATION,[0]),call(0x480e30,MANAGER,[ANIMATION+0x100]),call(0x480e80,MANAGER,[ANIMATION,0]),call(0x480df0,MANAGER,[ANIMATION])],p,label='asset packed references and manager pin unpin removal')

# Full original compressed-stream builds, including empty bones and all formats.
def streams(bones,flags,seed):
 r=random.Random(seed);rot=bytearray();trans=bytearray();rl=[];tl=[];rc=tc=0
 for bone in range(bones):
  before=len(rot)
  for key in range(r.randrange(4)):
   rc+=1;header=r.randrange(0x800)|(0x8000 if key&1 else 0)
   mode=r.randrange(9)
   if mode<8:header|=0x4000|(mode<<11)
   if flags&0x100:rot+=struct.pack('<H',r.getrandbits(16))
   rot+=struct.pack('<H',header)
   if header&0x4000 and not header&0x3800:rot+=bytes([r.randrange(256)])
   else:
    for shift in [13,12,11]:
     if header&0x4000 and header&(1<<shift) or flags&0x8000:rot+=bytes([r.randrange(256)])
     else:rot+=struct.pack('<H',r.getrandbits(16))
  rl.append(len(rot)-before);before=len(trans)
  for key in range(r.randrange(4)):
   tc+=1;header=r.randrange(256);trans+=bytes([header])
   if not header&0x40:trans+=struct.pack('<H',r.getrandbits(16))
   trans+=bytes([r.randrange(256)]) if header&0x80 else bytes(r.randrange(256) for _ in range(6))
  tl.append(len(trans)-before)
 p=[raw(KEYS,rot),raw(KEYS+0x1000,trans),patch(LENGTHS,'<'+'H'*(bones+1),*rl,0),patch(LENGTHS+0x100,'<'+'H'*(bones+1),*tl,0),patch(ANIMATION+4,'<2I',flags,bones),patch(ANIMATION+0xc,'<I',TABLE),patch(ANIMATION+0x34,'<2h',rc,tc),raw(TABLE,bytes(r.randrange(256) for _ in range(1536)))]
 return p
for i in range(72):
 fmt=[2,3,4][i%3];flags=sum(v for k,v in enumerate([0x100,0x2000,0x8000,0x10000,0x800]) if i&(1<<k));bones=[1,2,4,12,59][i%5]
 p=streams(bones,flags,i)+[patch(ANIMATION+0x3a,'<H',20)]
 changes={0x6fa2d8:i%12,0x7d1ed0:0 if i&1 else 1,0x7d1ed4:i//24,0x6fa2e0:0,0x6fa2e4:i//24}
 if i%9==0:p += [patch(CONTEXT+32,'<I',0)]
 case([call(0x485270,ANIMATION,[fmt])],p,changes,label='complete cache build formats flags empty bones and throttle')
for fmt in [2,3,4]:
 p=streams(5,0x8100,0x42)
 case([call(0x485270,ANIMATION,[fmt]),call(0x482ba0,ANIMATION),call(0x482bd0,ANIMATION,[0]),call(0x480df0,MANAGER,[ANIMATION]),call(0x485270,ANIMATION,[fmt])],p,pooled(1,1),label='decode pin unpin evict and rebuild lifecycle')
for fmt in [0,1,2,3,4,5,0xffffffff]:
 for priority in [0,20,0xff]:
  p=streams(4,0x10000,31)+[patch(MANAGER+0xc8,'<2I',50,50*4096),patch(ANIMATION+0x3a,'<H',priority<<1)]
  for i,b in enumerate(blocks):p+=active_block(b,ANIMATION+0x100+i*0x40,refs=i%3,timestamp=1+i,size=4096,storage=0)
  case([call(0x485270,ANIMATION,[fmt])],p,label='full cache build with signed priority eviction and all stride formats')
for count in [9,10,11,0xffffffff]:
 p=streams(1,0,17)
 case([call(0x485270,ANIMATION,[4])],p,{0x6fa2d8:count,0x6fa2e0:0xffffffff,0x6fa2e4:7,0x7d1ed0:0,0x7d1ed4:8},label='64-bit tick rollover resets full throttle')

adapter=out/'animation-cache-memory.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/animation_cache_memory.c'),'-o',str(adapter)],check=True)
scope='Thirty-two complete routines recover packed rotation/translation decoding, vector/quaternion expansion, cache allocation/ownership/eviction, pinning, a 64-bit tick accessor and the full throttled animation cache builder. Original game callees and the registered cache-clear callback execute unchanged. Heap selection, scope, allocation, release and contiguous availability are explicit host allocator boundaries. Full fixture memory/globals/heap records/returns compare exactly. Truly uninitialized expanded-record padding is explicitly zeroed and only those original local padding bytes are seeded; translation records preserve the last rotation key bytes from reused automatic storage. Tested streams cover 1..59 bones and all stride formats. Valid streams and terminating length tables within allocated buffers, initialized managers, clear busy flags and successful requested reader allocation are internal contracts. Animation file parsing, cache initialization, standard controller/factory/channel dispatch, full movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'animation-cache-memory.bin','memory_adapter':ADAPTER,'memory_fixture':adapter.name,'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_animation_cache_scope','fixture_animation_cache_available'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'function_exports':[[0x482b90,'thug_keyframe_animation_cache_cleared']],'pointer_fields':[b+0x20 for b in blocks]}
path=out/'animation-cache-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),sum(oracle.counts.values()),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_cache_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'heap_service_events':dict(services),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()),'new roots',len(NEW))
