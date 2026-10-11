"""Compare original multiline wrapping, drawable ordering and text-style pools."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'ui-drawing.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x20000
ADAPTER,CONTEXT,ALLOCATOR,FONT,METRICS,GLYPHS,BUTTON,BGLYPHS,BUCKETS,ENTRY,INPUT,ROWS,ROW_DATA,WIDGET,DRAW,STYLE,PARENTS,COPY,LOG,HEAP=[BASE+x for x in [0x100,0x200,0x400,0x2000,0x2400,0x3000,0x4c00,0x5000,0x6800,0x6900,0x7000,0x8000,0x9000,0xa000,0xb000,0xc000,0xd000,0xf000,0x11000,0x14000]]
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ALLOCATOR+0x11c,'<I',ALLOCATOR+0x200)
put(FONT,'<3I',0x64a328,0xaabbccdd,METRICS)
for at,glyphs,seed in [(METRICS,GLYPHS,1),(BUTTON,BGLYPHS,3)]:
 put(at,'<3I',17,0x12345678,glyphs)
 for i in range(296):put(at+12+i,'<B',(i*13+seed)&255)
 put(at+0x134,'<hh',1,4)
 for i in range(256):put(glyphs+i*24+16,'<H',2+(i*7+seed)%13)
# Two colliding nodes: the first has a matching ID but a null value.
put(BUCKETS,'<3I',0xabc,0,BUCKETS+16);put(BUCKETS+16,'<3I',0xabc,ENTRY,0);put(ENTRY+0x18,'<I',FONT)
put(WIDGET+0x178,'<I',0xabc);put(WIDGET+0x17c,'<I',ROWS)
for i in range(8):put(ROWS+i*4,'<I',ROW_DATA+i*128+4)
for i in range(8):
 at=DRAW+i*128;put(at,'<2I',0x64a89c,0);put(at+8,'<B',1);put(at+12,'<2f',float(i-4),0)
 at=STYLE+i*128;put(at,'<I',0x64a34c);put(at+0x44,'<2I',STYLE+(i+1)*128 if i<7 else 0,DRAW+i*128)
 at=PARENTS+i*256;put(at+4,'<I',0);put(at+0x18,'<I',0);put(at+0x4c,'<I',PARENTS+(i+1)*256 if i<7 else 0)
initial=bytes(memory);globals_=[];defaults=[];index={}
def glob(name,at,value=0,width=4,offset=0):
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
glob('thug_drawables',0x7cc248);glob('thug_text_draw_style_pool',0x6fa804)
glob('thug_font_table_shift',0x6fa9f0);glob('thug_font_buckets',0x6fa9f4,BUCKETS)
glob('thug_button_font',0x780fdc,BUTTON)
for i in range(32):glob('thug_button_glyphs',0x6fa808+i,ord('4'),1,i)
functions={}
def bind(at,name,argc=0,result='void',this=True,heap=False,floats=()):
 f={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap}
 if floats:f['float_args']=list(floats)
 functions[hex(at)]=f
bind(0x4af720,'thug_ui_wrap_text',1)
bind(0x4df900,'thug_drawable_insert');bind(0x4df950,'thug_drawable_unlink')
bind(0x4dfa70,'thug_drawable_initialize',2,'word');bind(0x4ceed0,'thug_text_drawable_initialize',1,'word')
bind(0x4dfae0,'thug_drawable_set_depth',1,floats=[0]);bind(0x4dfb20,'thug_drawable_set_priority',1,floats=[0]);bind(0x4dfb70,'thug_drawable_set_hidden',1)
bind(0x5480a0,'thug_draw_style_noop');bind(0x48d220,'thug_draw_style_initialize',1,'word')
bind(0x4b3f50,'thug_text_draw_style_data');bind(0x4b3db0,'thug_text_draw_style_order');bind(0x4b3da0,'thug_text_draw_style_visibility')
bind(0x48d1b0,'thug_draw_style_set_owner',1)
bind(0x4b3e70,'thug_text_draw_style_initialize',result='word',heap=True)
bind(0x4b3fd0,'thug_text_draw_style_populate',1,this=False,heap=True)
bind(0x48d1d0,'thug_text_draw_style_take',result='word',this=False)
bind(0x4a8b80,'thug_ui_parent_reference',1,'word');bind(0x4a8bb0,'thug_ui_text_ancestor',result='word')
bind(0x4a8730,'thug_ui_copy_layout_state',1,'word')
bind(0x4b0620,'thug_ui_allocate_text_styles',2,heap=True)
# Existing reference destruction closes the parent-output lifetime too.
bind(0x416dd0,'thug_object_reference_destroy')
observe=list(map(lambda k:int(k,16),functions))+[0x48d760,0x402170,0x48d060,0x4b3d10,0x4cecb0,0x4637c0,0x4637e0,0x4020e0,0x48d6a0,0x4b2160]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,scope_entries={ALLOCATOR+0x200:6})
fields={FONT,*[DRAW+i*128 for i in range(8)],*[STYLE+i*128 for i in range(8)]}
def constructed(cpu,address,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX))
for at in [0x4dfa70,0x48d220]:oracle.cpu.hook_add(UC_HOOK_CODE,constructed,begin=at,end=at)
exports=[[0x64a328,'thug_font_methods'],[0x64ad18,'thug_drawable_methods'],[0x64a89c,'thug_text_drawable_methods'],[0x648aa0,'thug_draw_style_base_methods'],[0x64a34c,'thug_text_draw_style_methods']]
labels=[];branches=Counter()
branch_at={0x4af7e6:'wrap_row',0x4af804:'trim_space',0x4af82c:'ring_reset',0x4df944:'insert_head',0x4df93a:'insert_later',0x4df959:'unlink_head',0x4df981:'unlink_later',0x4dfb4d:'priority_resets_depth'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]
def case(calls,patches=(),changes=None,label='drawing',float_fields=()):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  if float_fields:s['float_fields']=list(float_fields)
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original UI drawing cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x4af720)
# Start from existing lines too, as the original parent appends multiple strings.
def wrap_setup(text,limit=80,scale=1,capacity=3,row=0,old=b'',current_width=0,total=1):
 p=[raw(INPUT,text+b'\0'),patch(WIDGET+0x160,'<f',limit),patch(WIDGET+0x180,'<3I',total,row,len(old)),patch(WIDGET+0x18c,'<f',current_width),patch(WIDGET+0x190,'<i',capacity),patch(WIDGET+0x19c,'<f',scale)]
 for i in range(8):p.append(raw(ROW_DATA+i*128,b'\x20\x20\x20\x20'+(old if i==row else b'row'+str(i).encode())+b'\0'))
 return p
texts=[b'',b' ',b'   ',b'one two three',b'one\\_two three',b'\\n',b'\\n\\n',b'A\\nB\\n',b'word \\nnext',b'\\c1red \\C2blue',b'\\u0A \\U1B',b'\\s4 \\b4 \\B5 \\m2 \\M8',b'\\\\word test',b'x'*94+b' y',b'x'*95,b'first '+b'z'*95,b'a '*60]
for text in texts:
 for limit,scale in [(0,1),(1,1),(24,1),(80,1),(1024,1),(80,0.5),(80,0),(80,-1)]:
  for capacity,row,old,cw,total in [(1,0,b'',0,1),(3,2,b'existing ',70,0xfffffffe)]:
   case([call(0x4af720,WIDGET,[INPUT])]*2,wrap_setup(text,limit,scale,capacity,row,old,cw,total),label='wrap limits, escapes, newline deferral, ring reuse and repeated append')
# Byte length boundaries independent of measured width; signed capacity compare.
for n in [0,1,94,95]:
 for capacity in [-2147483648,-1,0,1,3]:
  p=wrap_setup(b'X',1e30,1,capacity,0,b'z'*n,0)
  case([call(0x4af720,WIDGET,[INPUT])],p,label='95-byte row boundary and signed capacity')
# Width equality uses strict greater; x87 intermediates retain extended exponent.
floatbits=[bits(v) for v in [0,-0.0,1,-1,0.5,1.000001,80,1e-30,1e30]]+[1,0x00800000,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc12345]
for i in range(160):
 p=wrap_setup(rng.choice([b'word word end',b' a b ',b'\\nX',b'\\s4 Z',b'']),old=b'old ',current_width=1)
 p += [patch(WIDGET+x,'<I',rng.choice(floatbits)) for x in [0x160,0x18c,0x19c]]
 case([call(0x4af720,WIDGET,[INPUT])],p,label='wrap float ordering and typed arithmetic NaNs',float_fields=[WIDGET+0x18c])
for i in range(40):
 text=b''.join(rng.choice([b'alpha ',b'\\_',b'\\n',b'\\s4',b'\\c1',b'z ']) for _ in range(16))
 case([call(0x4af720,WIDGET,[INPUT])],wrap_setup(text,rng.choice([20,40,80]),rng.choice([0.5,1,2]),rng.randrange(1,9)),label='mixed text token sequences')
# Width exactly at the boundary, just below, and just above it.
for spacing in [-32768,0,32767]:
 for limit in [29.999998,30,30.000002]:
  p=wrap_setup(b'A B ',limit,old=b'old ',current_width=10)
  p += [patch(METRICS+0x134,'<hh',spacing,0),patch(GLYPHS+((65*13+1)&255)*24+16,'<H',20)]
  case([call(0x4af720,WIDGET,[INPUT])],p,label='word width equality and signed spacing')
# Insertion/unlinking is tested on empty lists, ties, infinities and unordered depths.
def draw_setup(depths,hidden=False):
 p=[]
 for i,d in enumerate(depths):
  p += [patch(DRAW+i*128+4,'<I',DRAW+(i+1)*128 if i+1<len(depths) else 0),patch(DRAW+i*128+8,'<B',int(hidden)),patch(DRAW+i*128+12,'<I',d)]
 return p
special=[bits(x) for x in [-10,-1,-0.0,0,1,10]]+[0xff800000,0x7f800000,0x7fc12345,0xffc12345,0x7fa12345]
for old in [[],[bits(0)],[bits(-1),bits(0),bits(1)],[bits(0)]*3,[0x7fc12345,bits(0)],[bits(0),0x7fc12345],[0xff800000,0x7f800000]]:
 for depth in special:
  p=draw_setup(old)+[patch(DRAW+7*128+12,'<I',depth)]
  calls=[call(0x4df900,DRAW+7*128),call(0x4df950,DRAW+7*128),call(0x4df950,DRAW+7*128)]
  if old:calls+=[call(0x4df950,DRAW+(len(old)-1)*128),call(0x4df950,DRAW)]
  case(calls,p,{0x7cc248:DRAW if old else 0},'sorted insertion, unordered depths and absent-node unlink')
# Changes reorder only when required; hidden values compare their full low bytes.
for depth in special[:-1]:
 for other in special[:-1]:
  for hidden in [0,1]:
   p=draw_setup([bits(-2),depth,bits(2)])
   if hidden:p += [patch(DRAW+4,'<I',DRAW+256),patch(DRAW+128+8,'<B',1)]
   calls=[call(0x4dfae0,DRAW+128,[other])]*2+[call(0x4dfb20,DRAW+128,[other])]*2
   calls += [call(0x4dfb70,DRAW+128,[v]) for v in [257,2,256,0,255,1,0]]
   case(calls,p,{0x7cc248:DRAW},'depth/priority changes, stable equality and visibility byte flags')
# Constructor padding and raw depth bits are compared without NaN normalization.
for depth in special:
 for hidden in [0,1,2,255,256,257]:
  p=draw_setup([bits(-1),bits(1)])
  case([call(0x4dfa70,DRAW+256,[depth,hidden]),call(0x4ceed0,DRAW+384,[depth])],p,{0x7cc248:DRAW},'drawable constructors preserve raw words and padding')
# Base style leaves two words and derived storage untouched; concrete style
# allocates a real drawable and dispatches its actual three virtual updates.
for owner in [0,1,0xffffffff,0x80000000]:
 case([call(0x48d220,STYLE,[owner]),call(0x48d1b0,STYLE,[owner^0x12345678]),call(0x5480a0,STYLE)],label='base style constructor, owner virtual and original return-only method')
 case([call(0x4b3e70,STYLE),call(0x48d1b0,STYLE,[owner]),call(0x4b3e70,STYLE+128)],label='concrete style allocation and real virtual initialization')
for i in range(96):
 p=[]
 for offset in [0xc,0x10,0x14,0x18,0x1c,0x20,0x24,0x28,0x38]:p.append(patch(STYLE+offset,'<I',rng.getrandbits(32)))
 p += [patch(STYLE+4,'<2I',FONT if i&1 else 0,INPUT),patch(STYLE+0x3c,'<4B',i&255,0x6a,i%3,int(bool(i%4))),patch(STYLE+0x2c,'<I',rng.choice(special[:-1])),patch(STYLE+0x34,'<I',rng.choice([0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff,16777217,65537]))]
 # Start hidden; visibility puts the node into the real global list when needed.
 case([call(0x4b3f50,STYLE),call(0x4b3db0,STYLE),call(0x4b3da0,STYLE)]*2,p,label='style data, unsigned priority rounding and concrete visibility updates')
for count in [0,1,2,7,16,32]:
 for existing in [0,STYLE]:
  calls=[call(0x4b3fd0,args=[count])]+[call(0x48d1d0) for _ in range(count+(9 if existing else 2))]
  case(calls,changes={0x6fa804:existing},label='pool construction, LIFO acquisition, retained links and exhaustion')
# Parent references retain intrusive peer links, and ancestors exclude self.
REF,PEER=PARENTS+0x900,PARENTS+0xa00
for match in range(-1,8):
 for has_peer in [0,1]:
  p=[]
  for i in range(8):
   p += [patch(PARENTS+i*256+0x18,'<I',0xa13adbb7 if i==match else 0),patch(PARENTS+i*256+4,'<I',PEER+i*16 if has_peer else 0),patch(PEER+i*16,'<3I',PARENTS+i*256,0,0)]
  for start in [0,3,7]:
   case([call(0x4a8b80,PARENTS+start*256,[REF]),call(0x416dd0,REF),call(0x4a8bb0,PARENTS+start*256)]*2,p,label='parent reference lifetime and nearest matching ancestor')
for delta in [-67,-64,-4,-1,0,1,4,64,67,80]:
 for misalignment in range(4):
  data=bytes(rng.getrandbits(8) for _ in range(512));source=COPY+128+misalignment;dest=source+delta
  case([call(0x4a8730,dest,[source])]*2,[raw(COPY,data)],label='forward 17-word copy, unaligned pointers and overlapping propagation')
for count in [0,1,3]:
 for secondary in [0,1,255]:
  for only in [0,1,256,257]:
   for ancestor in [0,1]:
    if not count and secondary and ancestor:continue # Original dereferences an uninitialized zero-size array.
    p=[patch(WIDGET+0x4c,'<I',PARENTS if ancestor else 0),patch(PARENTS+256+0x18,'<I',0xa13adbb7),patch(PARENTS+256+0x178,'<I',0xfedcba98),patch(WIDGET+0x184,'<3I',ROWS,ROWS+32,2),patch(WIDGET+0x194,'<B',secondary),patch(ROWS,'<2I',STYLE+768,STYLE+896)]
    case([call(0x4b0620,WIDGET,[count,only])],p,{0x6fa804:STYLE},'widget style arrays, UI scopes, first-item owner propagation and byte-only mode')
# Exhausted pools are preserved as null entries when there is no owner dispatch.
case([call(0x4b0620,WIDGET,[3,0])],[patch(WIDGET+0x4c,'<I',0),patch(WIDGET+0x194,'<B',1)],label='widget allocation preserves exhausted pool returns')
scope='Twenty-one original routines for complete multiline word wrapping, sorted drawable lists, visibility/depth/priority updates, base and concrete text drawing construction, actual virtual style updates, reusable style pools, widget style-array allocation, parent references/ancestor lookup and forward layout-state copying. Existing reference destruction closes output lifetimes. Full arena/global bytes, returns, pointer relocation and heap/scope events compare. Only arithmetic NaNs in multiline accumulated width use classification; raw copied fields and padding remain exact. Heap services require an initialized adapter and successful allocation. Font lookup/measurement, tokenizer and reference callees execute unchanged. Drawable rendering/destruction and two concrete style virtual slots remain unavailable; no renderer or gameplay callback is substituted. The multiline parent, UI manager registration and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'ui-drawing-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'substituted_gameplay_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields)}
path=out/'ui-drawing-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_ui_drawing_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
