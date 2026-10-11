"""Original object/widget construction, parent attachment and drawing-pool return."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'ui-construction.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'ui-drawing-fixtures.json').read_text());BASE,SIZE=prior['base'],0x60000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
WIDGET,DRAW,STYLE=BASE+0xa000,BASE+0xb000,BASE+0xc000
OBJ,TREE,REF,POOL,BLOCKS,OWNED,ARRAYS,LOG,HEAP=[BASE+x for x in [0x10000,0x11000,0x16000,0x17000,0x17400,0x18000,0x1c000,0x20000,0x30000]]
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,OBJ+0x20,0)
for i in range(2):
 p=POOL+i*128;put(p,'<6I',BLOCKS+i*128,BLOCKS+(i+1)*128,0xaabb,0xccdd,0,BLOCKS+i*128);put(p+88,'<I',0)
 for j in range(8):put(BLOCKS+i*128+j*16,'<I',BLOCKS+i*128+(j+1)*16 if j<7 else 0)
for i in range(8):
 put(STYLE+i*128+8,'<2I',0,0);put(STYLE+i*128+0x3e,'<B',1)
 put(OWNED+i*256,'<I',i);put(ARRAYS+i*4,'<I',STYLE+i*128)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,width=4,offset=0):
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
glob('thug_object_default_id',0x64780c,0xffffffff);glob('thug_object_default_type',0x647810)
glob('thug_script_structure_pool_index',0x6f3614)
glob('thug_script_structure_pools',0x6f361c);glob('thug_script_structure_pools',0x6f3620,offset=4)
functions={}
def bind(at,name,argc=0,result='void',this=True,heap=False,floats=(),cleanup=None):
 f={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap}
 if floats:f['float_args']=list(floats)
 if cleanup is not None:f['cleanup']=cleanup
 functions[hex(at)]=f
bind(0x4637b0,'thug_reference_target_initialize',result='word')
bind(0x41d1d0,'thug_object_reference_assign',1,'word');bind(0x4a8f60,'thug_object_reference_assign_reference',1,'word')
bind(0x460b80,'thug_ui_object_initialize',result='word');bind(0x4611e0,'thug_ui_object_ensure_parameters',heap=True);bind(0x461970,'thug_ui_object_set_type',1,heap=True)
bind(0x4a8f90,'thug_ui_initialize',result='word');bind(0x4b0920,'thug_ui_text_initialize',result='word',heap=True)
bind(0x4a8f20,'thug_ui_has_inherited_owner',result='byte');bind(0x4aa390,'thug_ui_set_depth_tree',1,floats=[0]);bind(0x4aa470,'thug_ui_set_owner_tree',1);bind(0x4aa8e0,'thug_ui_set_parent',2)
bind(0x48d5a0,'thug_draw_style_clear_storage',heap=True);bind(0x48d5f0,'thug_text_draw_style_return',1,this=False,heap=True);bind(0x4b0760,'thug_ui_release_text_styles',1,heap=True)
# Existing integration entry points, all original callees rather than substitutes.
bind(0x4b3fd0,'thug_text_draw_style_populate',1,this=False,heap=True);bind(0x48d1d0,'thug_text_draw_style_take',result='word',this=False)
bind(0x4b0620,'thug_ui_allocate_text_styles',2,heap=True);bind(0x416dd0,'thug_object_reference_destroy')
observe=[int(k,16) for k in functions]+[0x4a8730,0x4b3e70,0x48d220,0x4dfa70,0x4b3f50,0x4b3db0,0x4b3da0,0x4dfb70,0x4df950,0x4a8bb0,0x4b2160,0x48d1b0,0x4637c0,0x4637e0,0x476410,0x5ba3d0,0x477d40,0x477480,0x5480a0,0x62382b]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,scope_entries={ALLOCATOR+0x200:6})
fields={BASE+0x2000,*[DRAW+i*128 for i in range(8)],*[STYLE+i*128 for i in range(8)],*[TREE+i*512 for i in range(8)]}
def constructed(cpu,address,size,user):
 at=cpu.reg_read(UC_X86_REG_ECX);fields.add(at)
 if address==0x460b80:fields.update([at+0x28,at+0x40])
for at in [0x4637b0,0x460b80,0x48d220,0x4dfa70]:oracle.cpu.hook_add(UC_HOOK_CODE,constructed,begin=at,end=at)
exports=prior['pointer_exports']+[[0x6478e4,'thug_reference_target_methods'],[0x6477e8,'thug_ui_object_methods'],[0x6477e4,'thug_ui_object_queue_methods'],[0x6477e0,'thug_ui_object_secondary_methods'],[0x64a090,'thug_ui_element_methods'],[0x64a290,'thug_ui_text_methods']]
labels=[];branches=Counter()
branch_at={0x461222:'selected_pool',0x461258:'initialize_parameters',0x461261:'empty_selected_pool',0x4aa966:'detach_found',0x4aaa3c:'append_after_sibling',0x4aaa41:'append_first',0x4aaaeb:'inherit_owner',0x48d5aa:'release_owned_word',0x48d5c4:'release_record_array',0x4b079d:'release_secondary_array',0x4b07ed:'release_primary_array'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]
def case(calls,patches=(),changes=None,label='UI construction',float_fields=()):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  if float_fields:s['float_fields']=list(float_fields)
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original UI construction cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x4b0920)
for fill in [0,0xa5,0xff,None]:
 data=bytes([fill])*0x1c0 if fill is not None else bytes(rng.getrandbits(8) for _ in range(0x1c0))
 for id_ in [0,1,0xffffffff,0x80000000]:
  for type_ in [0,0x12345678,0xffffffff]:
   p=[raw(OBJ,data)];changes={0x64780c:id_,0x647810:type_}
   for fn in [0x4637b0,0x460b80,0x4a8f90]:case([call(fn,OBJ)]*2,p,changes,'constructors preserve opaque fields and copy uninitialized state words')
   case([call(0x4b0920,OBJ)],p,{**changes,0x6fa804:STYLE},'complete text constructor, pool acquisition, parameters and defaults')
# Pool selected/alternate identities, signed usage counters, null exhaustion,
# preexisting parameters and repeated construction/setter operations.
for selected in [0,1]:
 for p0,p1 in [(0,0),(POOL,0),(0,POOL+128),(POOL,POOL+128)]:
  for empty in [False,True]:
   p=[patch(OBJ+0x20,'<I',0)]
   if empty:p += [patch(POOL+20,'<I',0),patch(POOL+128+20,'<I',0)]
   changes={0x6f3614:selected,0x6f361c:p0,0x6f3620:p1}
   case([call(0x4611e0,OBJ)]*2,p,changes,'lazy parameter allocation and exhausted selected pool')
   if not empty or not [p0,p1][selected]:
    for t in [0,0xffffffff,0x5200dfb6]:
     case([call(0x461970,OBJ,[t]),call(0x461970,OBJ,[t^0xffffffff])],p,changes,'type setter executes checksum replacement through actual component ownership')
for count,peak in [(0,0),(0x7fffffff,0),(0xffffffff,0x7fffffff)]:
 case([call(0x4611e0,OBJ)],[patch(OBJ+0x20,'<I',0),patch(POOL+16,'<I',count),patch(POOL+88,'<I',peak)],{0x6f361c:POOL},'structure pool usage and peak signed comparison')
for t in [0,1,13,0xffffffff]:
 p=[patch(OBJ+0x20,'<I',OWNED),patch(OWNED,'<2I',0xa5a500a5,OWNED+32),patch(OWNED+32,'<4I',0x1a,0x7321a8d6,t,0)]
 case([call(0x4611e0,OBJ),call(0x461970,OBJ,[t]),call(0x461970,OBJ,[0x12345678])],p,label='preexisting parameters preserve header bytes and replace actual checksum component')
# Build real intrusive references for the parent/sibling tree and external handles.
def tree_setup(parents=(-1,-1,0,0,0,2,2,1),flags=None,depths=None,owners=None):
 data=bytearray(8*512);refs=bytearray(9*16);children=[[] for _ in parents]
 def write(at,fmt,*values):
  target,offset=(data,at-TREE) if TREE<=at<TREE+len(data) else (refs,at-REF)
  struct.pack_into(fmt,target,offset,*values)
 def word(at):return struct.unpack_from('<I',data,at-TREE)[0]
 def link(at,target):
  write(at,'<3I',target,0,0)
  if target:
   head=word(target+4);write(at+8,'<I',head)
   if head:write(head+4,'<I',at)
   write(target+4,'<I',at)
 for i,p in enumerate(parents):
  at=TREE+i*512;write(at,'<I',0x64a090);write(at+8,'<I',flags[i] if flags else 0);write(at+0x14,'<I',0x100+i)
  write(at+0x16c,'<I',depths[i] if depths else bits(float(i)));write(at+0x174,'<I',owners[i] if owners else 0x200+i)
  if p>=0:children[p].append(i)
 for i,p in enumerate(parents):
  at=TREE+i*512;link(at+0x4c,TREE+p*512 if p>=0 else 0)
  link(at+0x58,TREE+children[i][0]*512 if children[i] else 0)
  sib=children[p] if p>=0 else [];index_=sib.index(i) if sib else -1
  link(at+0x64,TREE+sib[index_+1]*512 if sib and index_+1<len(sib) else 0)
  link(at+0x70,TREE+sib[index_-1]*512 if index_>0 else 0)
 for i in range(8):link(REF+i*16,TREE+i*512)
 return [raw(TREE,data),raw(REF,refs)]
# Both reference assignment forms, including self-reference source and peer order.
for src in range(9):
 for dst in [0,3,7,8]:
  p=tree_setup()
  case([call(0x4a8f60,REF+dst*16,[REF+src*16])]*2+[call(0x416dd0,REF+dst*16)],p,label='reference source aliasing, replacement, self-clear and peer restoration')
  case([call(0x41d1d0,REF+dst*16,[TREE+src*512 if src<8 else 0])]*2+[call(0x416dd0,REF+dst*16)],p,label='object reference replacement and same-target reordering')
for mask in [0,1,2,4,8,0x80,0xff]:
 flags=[0x10000000 if mask>>i&1 else 0 for i in range(8)]
 case([call(0x4a8f20,TREE+i*512) for i in range(8)],tree_setup(flags=flags),label='inherited owner flag across all ancestors')
floatbits=[bits(v) for v in [0,-0.0,1,-1,0.5,16777216,16777218,1e-30,1e30]]+[0x7f7fffff,1,0x7f800000,0xff800000,0x7fc12345,0xffc12345]
for fixed in [0,1,4,0xff]:
 for value in floatbits:
  flags=[0x8000 if fixed>>i&1 else 0 for i in range(8)];p=tree_setup(flags=flags)
  case([call(0x4aa390,TREE,[value])]*2,p,label='recursive depth, fixed nodes, rounding and arithmetic NaNs',float_fields=[TREE+i*512+0x16c for i in [2,3,4,5,6]])
for owner in [0,1,0xffffffff,0x80000000]:
 case([call(0x4aa470,TREE,[owner])]*2,tree_setup(),label='owner propagation through linked children and siblings')
parents=[-1,-1,0,0,0,2,2,1]
for child in range(8):
 for parent in range(-1,8):
  at=parent
  while at>=0 and at!=child:at=parents[at]
  if at==child:continue
  for inherited in [False,True]:
   p=tree_setup(flags=[0x10000000 if inherited and i in [0,1] else 0 for i in range(8)])
   target=REF+(parent if parent>=0 else 8)*16
   calls=[call(0x4aa8e0,TREE+child*512,[target,0]),call(0x4aa8e0,TREE+child*512,[target,0xffffffff]),call(0x4aa8e0,TREE+child*512,[REF+8*16,1])]
   case(calls,p,label='complete parent detach/append, repeated attachment and subtree propagation')
# Input can alias the parent's own intrusive reference and is reread later.
for offset in [0x4c,0x70]:
 case([call(0x4aa8e0,TREE+3*512,[TREE+3*512+offset,1])],tree_setup(flags=[0x10000000]*8),label='parent input aliases child reference fields')
# Missing membership is tolerated by the original scan before assigning a new parent.
# Relinking consistent intrusive lists needs explicit unlink of this old root handle.
# Clear its old node through the original reference destructor before the parent call.
case([call(0x416dd0,TREE+0x58),call(0x4aa8e0,TREE+3*512,[REF+16,0])],tree_setup(),label='old parent has no reachable child chain')
# Raw root depth is copied, arithmetic descendant depths alone allow NaN classification.
for value in floatbits:
 p=tree_setup(depths=[value]*8,flags=[0x8000 if i==2 else 0 for i in range(8)])
 case([call(0x4aa8e0,TREE+2*512,[REF+16,0])],p,label='parent depth arithmetic and fixed child propagation',float_fields=[TREE+i*512+0x16c for i in [2,5,6]])
# Owned storage cleanup includes empty record arrays and reverse noop destruction.
for owned in [0,OWNED+128]:
 for records in [0,OWNED+4]:
  for count in [0,1,7,0xffffffff]:
   p=[patch(STYLE+8,'<2I',records,owned),patch(OWNED,'<I',count)]
   case([call(0x48d5a0,STYLE)]*2,p,label='style owned buffers, zero and signed record counts, repeated cleanup')
   for hidden in [0,1,2]:
    p2=p+[patch(STYLE+0x3e,'<B',hidden),patch(DRAW+8,'<B',hidden),patch(DRAW+4,'<I',0)]
    case([call(0x48d5f0,args=[STYLE]),call(0x48d1d0)],p2,{0x7cc248:DRAW if not hidden else 0},'pool return hides actual drawable before freeing owned data')
for count in [-1,0,1,3]:
 for secondary in [0,ARRAYS+16]:
  for mode in [0,1,256,257]:
   p=[patch(WIDGET+0x184,'<3I',ARRAYS,secondary,count&0xffffffff)]
   for i in range(8):p += [patch(STYLE+i*128+8,'<2I',OWNED+i*256+4,OWNED+i*256+128),patch(OWNED+i*256,'<I',i),patch(STYLE+i*128+0x44,'<I',0)]
   case([call(0x4b0760,WIDGET,[mode])],p,label='widget style release modes, signed counts and retained primary pointer')
# Full lifecycle: actual pool construction -> text widget -> secondary styles ->
# release -> reacquire. Zeroed storage is what the original multiline caller uses.
for selected in [0,1]:
 p=[raw(OBJ,bytes(0x1b0))]
 changes={0x6f3614:selected,0x6f361c:POOL,0x6f3620:POOL+128}
 calls=[call(0x4b3fd0,args=[8]),call(0x4b0920,OBJ),call(0x4b0760,OBJ,[0]),call(0x4b0620,OBJ,[3,0]),call(0x4b0760,OBJ,[0]),call(0x48d1d0)]
 case(calls,p,changes,'constructed pool/widget acquisition, release and actual reuse')
for count in [1,3]:
 p=[raw(OBJ,bytes(0x1b0)),patch(OBJ+0x194,'<B',1)]
 calls=[call(0x4b3fd0,args=[8]),call(0x4b0620,OBJ,[count,0]),call(0x4b0760,OBJ,[1]),call(0x4b0620,OBJ,[count,1]),call(0x4b0760,OBJ,[0])]
 case(calls,p,label='secondary styles released and reacquired while primary styles remain live')
scope='Fifteen original routines for full base-object/UI/text-widget construction, lazy pooled parameters and type setting, both intrusive reference assignments, inherited owner/depth propagation, complete parent attachment, drawing storage cleanup, style-pool return and widget style-array release. Four existing lifecycle entry points exercise construction/acquisition/release/reuse. Whole arena/global bytes, returns, heap/scope order and real virtual visibility methods compare. Only typed arithmetic descendant depths use NaN classification; constructor padding, copied root fields and retained dangling primary-array pointers remain exact. Called game functions execute with initialized heap services; no gameplay/native virtual callback is substituted. Valid acyclic trees and sufficient pools/storage retain the original contracts. Widget destruction, UI registration, rendering and playable training integration remain unfinished.'
fixture={'base':BASE,'memory':'ui-construction-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'substituted_gameplay_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields)}
path=out/'ui-construction-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_ui_construction_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
