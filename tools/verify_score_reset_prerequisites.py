"""Original score cleanup, special-meter setup and concrete UI prerequisites."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'score-reset-prerequisites.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'event-delivery-fixtures.json').read_text());BASE=prior['base'];SIZE=0x1c0000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,PRINT,LOG,HEAP=BASE+0x10000,BASE+0x35f00,BASE+0x60000,BASE+0x80000
SCORE,GAME,NODES,BODIES,MAP,HOLDER,ITEMS,KEY,FONTS,UI,REF,COMPONENT,INPUT,GRAPH=[BASE+x for x in [0x180000,0x182000,0x183000,0x184000,0x188000,0x188100,0x188200,0x188300,0x188400,0x189000,0x18a000,0x18a100,0x18a200,0x190000]]
ENTRY,PROGRAM,EM,ELOG,SCRIPT,EVENTS,HANDLERS,OWNER,OTHER=BASE+0x2000,BASE+0x40000,BASE+0x130000,BASE+0x130020,BASE+0x144000,BASE+0x142000,BASE+0x142400,BASE+0x8000,BASE+0x8200

def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,BASE+0x100000,0,LOG,BASE,BASE+SIZE,0,0)
put(GAME+0x34,'<I',NODES);put(COMPONENT+12,'<I',BODIES)
for i in range(8):
 put(NODES+i*16,'<4I',0,BODIES+i*0x400,0,NODES+(i+1)*16)
 put(BODIES+i*0x400+0x14,'<I',0x100+i)
put(NODES+128,'<4I',0,0xffffffff,0,NODES+128)
for i in range(8):put(UI+i*0x100+0x4c,'<I',UI+(i+1)*0x100 if i<7 else 0)
put(UI+0x14,'<I',0x200);put(HOLDER,'<I',MAP)
memory[FONTS-BASE:FONTS-BASE+0x400]=bytes(0x400)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,width,value,offset in [('thug_game_context',0x7ce478,4,GAME,0),('thug_font_table_shift',0x6fa9f0,4,2,0),('thug_font_buckets',0x6fa9f4,4,FONTS,0)]+[('thug_button_glyphs',0x6fa808+i,1,(i*31+7)&255,i) for i in range(32)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
functions={}
def bind(at,name,argc=0,result='void',this=True,heap=False,diag=False,cleanup=None):
 f={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap}
 if cleanup is not None:f['cleanup']=cleanup
 if diag:f.update(stack_args=list(range(argc)),diagnostics=True)
 functions[hex(at)]=f
bind(0x566600,'thug_game_skater_by_id',1,'word');bind(0x57fec0,'thug_skater_screen_id',result='word')
bind(0x562920,'thug_score_entries_clear',heap=True);bind(0x563020,'thug_score_combo_clear',heap=True)
bind(0x562970,'thug_score_map_remove',1,heap=True);bind(0x5633e0,'thug_score_map_clear',heap=True)
bind(0x5612d0,'thug_score_configure_special');bind(0x518390,'thug_score_event_reset',heap=True,diag=True)
bind(0x4020e0,'thug_text_digit',1,'word',False);bind(0x48d6a0,'thug_text_button_glyph',1,'byte',False)
bind(0x48d760,'thug_font_find',1,'word',False);bind(0x4aae20,'thug_ui_find',3,'word',False,cleanup=12)
bind(0x4a8f40,'thug_ui_is_hidden',result='byte');bind(0x4a8940,'thug_ui_set_events_enabled',1,heap=True,diag=True)
bind(0x416dd0,'thug_object_reference_destroy')
observe=list(map(lambda n:int(n,16),functions))+[0x557f10,0x479070,0x478f00,0x46cc30,0x472e20,0x462f00,0x473800,0x460470,0x475750,0x4750b0,0x474540,0x4637c0,0x4637e0,0x462120]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=10000000,
 scope_entries={BASE+0x6000:1,ALLOCATOR+0x300:2,ALLOCATOR+0x400:4})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.setword(0x68ecfc,BASE+0x9600)
labels=[];fields=set(prior['pointer_fields']);exports=dict(prior['pointer_exports']);outcomes=Counter()
branches={0x5183ae:'score_event_emitted',0x5183db:'score_counter_reset',0x5629b8:'map_node_freed',0x563423:'map_payload_freed',0x4aae53:'widget_reference_found',0x4aaeb9:'widget_reference_missing'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
class Build:
 def __init__(self):self.data=bytearray();self.extra=[];self.buckets={}
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GRAPH+len(self.data)<BASE+SIZE;return at
 def array(self,kind,items):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items))
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items),value))
 def symbol(self,name,kind,value):
  bucket=BUCKETS+(name&4095)*4;old=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  self.buckets[bucket]=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,old))
 def patches(self):return [raw(GRAPH,self.data)]+[patch(at,'<I',v) for at,v in self.buckets.items()]+self.extra

def call(fn,this=SCORE,args=()):return fn,this,[x&0xffffffff for x in args]+([PRINT] if functions[hex(fn)].get('diagnostics') else [])
def case(calls,p=(),b=None,label='score/UI prerequisites',changes=None,float_fields=None):
 stages=oracle.case(calls,(b.patches() if b else [])+list(p),{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  if float_fields:s['float_fields']=float_fields
  merged=[]
  for at,data in s['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in exports:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original score/UI cases:',len(labels),flush=True)
 return stages
# Every character byte, including signed-high-byte inputs and base32 boundaries.
for value in range(256):case([call(0x4020e0,args=[INPUT]),call(0x48d6a0,args=[INPUT])],[raw(INPUT,bytes([value,ord('1'),0]))],label='single base32 character and button map')
# Skater searches retain the first matching ID, regardless of the local-player flag.
for count in [0,1,4,8]:
 for wanted in [0,0x100,0x102,0x107,0xffffffff,0xffff8000]:
  p=[patch(NODES+count*16+4,'<I',0xffffffff)]
  if count>2:p.append(patch(BODIES+2*0x400+0x14,'<I',0x100))
  case([call(0x566600,GAME,[wanted])],p,label='sentinel skater lookup first duplicate match and misses')
for value in [0,1,0xffffffff,0x80000000]:case([call(0x57fec0,BODIES)],[patch(BODIES+0x2b8,'<I',value)],label='screen identifier raw word')
# Signed entry count: release every stored pointer (including null), retain the
# backing array and capacity, always zero count. Full combo reset then repeats.
for count in [0,1,5,0xffffffff,0x80000000]:
 for nulls in [False,True]:
  p=[patch(SCORE+0x4c,'<3I',ITEMS,0x13579bdf,count),patch(HOLDER,'<I',SCORE+0x4c)]
  p += [patch(ITEMS+i*4,'<I',0 if nulls and i&1 else BODIES+i*32) for i in range(5)]
  case([call(0x562920,HOLDER)]*2,p,label='entry ownership with signed counts and null payloads')
  case([call(0x563020)]*2,p,label='whole combo reset exact field and history boundaries')
# Indexed map removal includes cache/key aliasing, head/middle/tail, duplicates,
# missing keys and preserved tail/index. Clearing frees nodes before payloads.
def map_data(count,duplicate=False,nulls=False):
 p=[patch(MAP,'<5I',count,ITEMS if count else 0,ITEMS+(count-1)*16 if count else 0,ITEMS if count else 0,0)]
 for i in range(count):p.append(patch(ITEMS+i*16,'<3I',0x1234 if duplicate else i,0 if nulls and i&1 else BODIES+i*32,ITEMS+(i+1)*16 if i+1<count else 0))
 return p
for count in [0,1,4,6]:
 for duplicate in [False,True]:
  for wanted in [0,1,3,5,0x1234,0xdeadbeef]:
   p=map_data(count,duplicate)+[patch(KEY,'<I',wanted)]
   case([call(0x562970,MAP,[KEY])]*2,p,label='shared map remove and stale cache invalidation')
  for key in [MAP,MAP+4,MAP+8,MAP+12,MAP+16]:
   case([call(0x562970,MAP,[key])],map_data(count,duplicate),label='key aliases changed or retained manager words')
  for nulls in [False,True]:case([call(0x5633e0,HOLDER)]*2,map_data(count,duplicate,nulls),label='full tracked-value map cleanup')
for count in [0xffffffff,0x80000000]:case([call(0x5633e0,HOLDER)],[patch(MAP,'<5I',count,0,0,0,99)],label='negative map count skips clearing')
# Original global array/number getters execute. Inline one-item arrays ignore
# indices; multi-item colors truncate low bytes; output float is the sole NaN field.
for inline in [False,True]:
 for kind in [1,2]:
  for number in [0,1,0xffffffff,0x80000000,0x3f800000,0x7f800000,0x7f812345,0xffc12345]:
   b=Build();colors=[b.array(1,[0x12345600+i,0xabcdef80+i,0xfffffffe,0x100]) if not inline else b.array(1,[0xface00a5+i]) for i in range(3)]
   b.symbol(0x2e8b9f1c,12,b.array(12,colors[:1] if inline else colors));b.symbol(0x3abcda81,kind,number)
   case([call(0x5612d0)]*2,b=b,label='special colors and typed numeric global rate',float_fields=[SCORE+0x88])
# Font hash lookup uses the original bucket stride, low-five-bit shift and
# nonnull matching values; a matching null value does not hide a later match.
for shift in [0,1,2,32,33,34]:
 for key in [0,1,2,3,7]:
  for match in ['head','chain','none','null_then_chain']:
   slot=key&((1<<(shift&31))-1);node=FONTS+slot*12;p=[];value=BODIES
   p += [patch(node,'<3I',key if match in ['head','null_then_chain'] else key+100,value if match=='head' else 0,FONTS+0x100),patch(FONTS+0x100,'<3I',key if match!='none' else key+200,value,0),patch(value+0x18,'<I',0xdeadbeef)]
   case([call(0x48d760,args=[key])],p,changes={0x6fa9f0:shift},label='font bucket lookup collisions and null values')
# Returned references are actual intrusive links, including preexisting peers.
for key in [0,1,2,0xffffffff]:
 for peers in [0,1,3]:
  p=[patch(OWNER+4,'<I',REF+0x100 if peers else 0)]
  for i in range(peers):p.append(patch(REF+0x100+i*12,'<3I',OWNER,REF+0x100+(i-1)*12 if i else 0,REF+0x100+(i+1)*12 if i+1<peers else 0))
  case([call(0x4aae20,args=[REF,key,0xffffffff]),call(0x416dd0,REF)],p,label='UI lookup and actual linked-reference lifetime')
for length in [1,2,8]:
 for hidden in [-1,0,1,7]:
  p=[patch(UI+(length-1)*256+0x4c,'<I',0)]
  p += [patch(UI+i*256+8,'<I',0x400000 if i==hidden else 0x123456) for i in range(length)]
  case([call(0x4a8f40,UI)],p,label='hidden state inherits parent flags')
# Build a genuine spawned script whose event handler runs original cached QB.
# All handlers below are bytecode5/6/7, never a native substitute.
def script_data(event,handler,flags=1):
 b=bytearray(244);struct.pack_into('<3I',b,12,PROGRAM+0x1000,SCRIPT+0x100,SCRIPT+0x110)
 struct.pack_into('<I',b,0x2c,SCRIPT+0x1c);struct.pack_into('<I',b,0x94,SCRIPT+0x34)
 struct.pack_into('<I',b,0xa4,3);struct.pack_into('<I',b,0xa8,event);struct.pack_into('<I',b,0xb0,0xabc)
 struct.pack_into('<I',b,0xc8,5);b[0xcc]=flags;struct.pack_into('<I',b,0xd4,0x200);struct.pack_into('<I',b,0xe0,EVENTS if handler else 0);struct.pack_into('<I',b,0xec,0x6478e4)
 p=[raw(SCRIPT,b),patch(SCRIPT+0x100,'<6I',0,0,0,0,0,0),patch(EVENTS,'<IIBBHI',HANDLERS,1,1,0,0,0),patch(HANDLERS,'<5I',event,handler,0,0,0),patch(ENTRY+8,'<I',2)]
 return p,{0x6f3538:SCRIPT,0x6f353c:1}
for target in [0x200,0x201,0xffffffff]:
 for flags in [0,1,2,3]:
  for handler in [0,5,6,7]:
   p,c=script_data(0x813cc576,handler,flags);p.append(patch(BODIES+0x2bc,'<I',(target-0x83321dea)&0xffffffff))
   case([call(0x518390,COMPONENT)]*2,p,changes=c,label='score event guard, exact script target, QB handlers and final counter reset')
for old in [0,0x4000,0xff004000]:
 for enabled in [0,1,2,256,257,0xffffffff]:
  for handler in [0,6]:
   event=0x3056434f if enabled==1 else 0x4a57316b;p,c=script_data(event,handler)
   p.append(patch(UI+8,'<I',old))
   case([call(0x4a8940,UI,[enabled])]*2,p,changes=c,label='UI event enable full-word comparisons and real QB event delivery')
fields.update(at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in exports)
scope='Fourteen original score/UI prerequisites: skater ID/screen lookup, owned trick-list cleanup and combo reset, shared indexed-map removal/clear, special-meter configuration, guarded spawned-script event reset, base32 character/button mapping, font lookup, widget reference lookup, inherited hidden state and UI event-enable mutation. Real script, lookup, reference, parameter, event delivery and heap callees execute; QB event handlers use actual cached bytecode, with no native gameplay callback substitution. Complete arena/global bytes, returns and heap/scope order compare. Only the special-rate float permits typed NaN classification. Valid sentinel/acyclic lists, required arrays, resolved event targets and successful allocation retain original contracts. Full score reset still needs text formatting/layout; activation, movement and rendering remain unfinished.'
fixture={'base':BASE,'memory':'score-reset-prerequisites-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':prior['pointer_exports'],'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals']}
path=out/'score-reset-prerequisites-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_score_reset_prerequisites_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/prior['memory'],out/'event-delivery-fixtures.json']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
