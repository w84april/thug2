"""Original profile/binding and full objective text-update call chains."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-text.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x100000
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
GAME,MANAGER,PROFILE,OTHER,SKATERS,BODY,OBJECT,OUTPUT,RAWARRAY,ITEMS,INPUT,TLS,LOCALE,SYMBOLS,GRAPH,LOG,HEAP=[BASE+x for x in [0x1000,0x2000,0x3000,0x4000,0x5000,0x6000,0x7000,0x10000,0x12000,0x13000,0x14000,0x15000,0x16000,0x20000,0x30000,0x60000,0xb0000]]
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(ALLOCATOR+0x124,'<I',ALLOCATOR+0x200)
put(MANAGER+0x14,'<3I',PROFILE,OTHER,0);put(GAME+0x34,'<I',SKATERS)
put(SKATERS,'<4I',0,BODY,0,SKATERS+16);put(SKATERS+16,'<4I',0,0xffffffff,0,SKATERS+16);put(BODY+0xbc,'<B',1)
for at in [TLS,LOCALE]:memory[at-BASE:at-BASE+256]=bytes(256)
put(TLS+0x64,'<I',LOCALE)
memory[SYMBOLS-BASE:SYMBOLS-BASE+16384]=bytes(16384)
initial=bytes(memory)
globals_=[['thug_game_context',0x7ce478,4],['thug_profile_manager',0x7ce4b4,4],['thug_script_symbol_buckets',0x6f3624,4],['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],['thug_script_string_interning',0x6f3570,1]]
defaults=[GAME,MANAGER,SYMBOLS,0,0,0];functions={}
def bind(at,name,argc=0,result='word',heap=False,this=True):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
bind(0x57b630,'thug_profile_current');bind(0x57b640,'thug_profile_at',1);bind(0x564f80,'thug_game_profile',1)
bind(0x586110,'thug_profile_parameters',1);bind(0x5860a0,'thug_profile_binding_count')
bind(0x587100,'thug_profile_binding_initialize');bind(0x586630,'thug_profile_binding',2,'void')
for at,name in [(0x476620,'text_forward'),(0x476ec0,'checksum_legacy'),(0x476f10,'array_legacy')]:bind(at,'thug_script_get_'+name,3,'byte')
bind(0x478b00,'thug_script_set_array_copy',2,'void',True);bind(0x46cb10,'thug_script_array_set_word',2,'void')
bind(0x555b50,'thug_objective_text_tables',4,'byte',True,False);bind(0x554890,'thug_objective_expand_text',5,'void',False,False);bind(0x556a00,'thug_objective_update_text',0,'byte',True)
observe=set(int(k,16) for k in functions)|{0x476590,0x476630,0x476950,0x4767c0,0x476860,0x476cb0,0x476af0,0x476b40,0x46cc30,0x46cb70,0x4779d0,0x477920,0x477140,0x478a60,0x4787a0,0x4763a0,0x479020,0x479070,0x566520,0x6234fe}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=sorted(observe),event_limit=(HEAP-LOG)//48)
# Model Windows TLS/last-error, as in the established CRT oracle. sprintf runs.
os_calls=Counter();last_error=0x12345678
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7);oracle.setword(0x68ecfc,LOCALE)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
def os_service(cpu,address,size,user):
 global last_error
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:cpu.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
 elif address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
 else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for at in [GET_ERROR,GET_TLS,SET_ERROR]:oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=at,end=at)
undefined_padding=0
# Only the output record's bytes9..11 come from an uninitialized stack local.
# Normalize those three bytes before fixture capture; both checksums/flag are exact.
def binding_padding(cpu,address,size,user):
 global undefined_padding
 target=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4)
 if BASE<=target<=BASE+SIZE-12:cpu.mem_write(target+9,bytes(3));undefined_padding+=3
oracle.cpu.hook_add(UC_HOOK_CODE,binding_padding,begin=0x586709,end=0x586709)
labels=[];outcomes=Counter()
branches={0x555bd9:'integer_binding',0x555bf0:'fallback_search',0x555c25:'fallback_match',0x555c1b:'binding_failure',0x555c87:'special_name',0x555cb1:'global_name',0x5548ec:'trick_markers',0x554948:'key_markers',0x556a77:'backup_main_string',0x556a9c:'backup_main_array',0x556ce6:'rewrite_success',0x556ca8:'rewrite_failure_cleanup',0x556d06:'main_string_original_retained',0x556db0:'main_array_formatted'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(fn,this=OBJECT,args=()):return fn,this,[x&0xffffffff for x in args]
def case(calls,p=(),b=None,label='objective text'):
 stages=oracle.case(calls,(b.patches() if b else [])+list(p));labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original text cases:',len(labels),flush=True)
 return stages
class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.extra=[]
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GRAPH+len(self.data)<LOG;return at
 def text(self,data):return self.alloc(data+b'\0')
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2+(i&1),0x5a,0,name,value&0xffffffff,0)) for i,(name,kind,value) in enumerate(entries)]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<II',0xabcdef01,nodes[0] if nodes else 0))
 def array(self,kind,items,count=None):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items)) if items else 0
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items) if count is None else count,value))
 def header(self,at,structure):self.extra.append(raw(at,self.data[structure-GRAPH:structure-GRAPH+8]))
 def symbol(self,name,kind,value):
  bucket=SYMBOLS+(name&4095)*4;at=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,self.buckets.get(bucket,0)));self.buckets[bucket]=at
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(at,'<I',v) for at,v in self.buckets.items()]+self.extra
# Accessor offsets, signed/wrapping indices in mapped memory and absent outputs.
for index in [0,1,0xffffffff,0x40000000,0x40000001]:
 at=(MANAGER+0x14+((index*4)&0xffffffff))&0xffffffff
 case([call(0x57b640,MANAGER,[index])],[patch(at,'<I',OTHER)],label='profile table uint32 address math')
for index in [0,1]:case([call(0x57b630,MANAGER)],[patch(MANAGER+0x1c,'<I',index)],label='current profile index')
for value in [None,0,1]:
 b=Build();params=b.structure([] if value is None else [(0x5b8ab877,1,value)])
 case([call(0x564f80,GAME,[params]),call(0x564f80,GAME,[0])],b=b,label='optional profile selector and default')
for value in [None,0,1,0xffffffff,0x80000000]:
 b=Build();nested=b.structure([]);root=b.structure([] if value is None else [(0xac9b9eda,1,value),(0x1234,10,nested)]);b.header(PROFILE+0x5c,root)
 case([call(0x5860a0,PROFILE),call(0x586110,PROFILE,[0x1234]),call(0x586110,PROFILE,[0])],b=b,label='missing profile outputs retain original seed')
for value in [0,1,0x7f,0xff]:case([call(0x587100,OUTPUT)],[patch(OUTPUT+8,'<I',0xabcdef00|value)],label='binding initializer preserves checksum and padding words')
# Legacy getters exercise all supported and missing forms, output aliases.
for kind in [1,3,10,12,13]:
 for flag in [0,1,0x100,0x101,0xffffffff]:
  b=Build();payload=b.text(b'legacy') if kind==3 else b.array(13,[1,2]) if kind==12 else b.structure([]) if kind==10 else 0x12345678
  root=b.structure([(1,kind,payload)])
  for fn in [0x476620,0x476ec0,0x476f10]:
   case([call(fn,root,[1,OUTPUT,flag]),call(fn,root,[2,OUTPUT+4,flag])],b=b,label='legacy getter types byte assertions and missing output retention')
# Binding output, optional boolean values, inline/multi-item storage and output alias.
for count in [1,3]:
 for index in range(count):
  for special in [None,0,1,2,0xffffffff]:
   b=Build();entries=[]
   for i in range(count):
    fields=[(0x5b077ce1,13,0x100+i),(0xa92a2280,13,0x200+i)]
    if special is not None:fields.append((0xb56a8816,1,special))
    entries.append(b.structure(fields))
   arr=b.array(10,entries);root=b.structure([(0xddbee809,10,b.structure([(0,12,arr)]))]);b.header(PROFILE+0x5c,root)
   for output in [OUTPUT,PROFILE+0x5c]:case([call(0x586630,PROFILE,[output,index])],b=b,label='binding copy with three documented undefined padding bytes')
# Word setter: inline ignores any index; multi-item writes use byte address wrap.
for count in [0,1,4]:
 for index in [0,1,3,0xffffffff,0x40000001]:
  case([call(0x46cb10,RAWARRAY,[index,0xdeadbeef])],[patch(RAWARRAY,'<3I',0x12345678,count,ITEMS)],label='array raw setter inline index ignoring and wrapped writes')
# Array deep copy before aliasing replacement, including nested ownership.
for kind in [1,2,3,10,12,13]:
 for count in [0,1,3]:
  b=Build();values=[]
  for i in range(count):
   values.append(b.text(b'array/text') if kind==3 else b.structure([(1,1,i)]) if kind==10 else b.array(13,[i,i+1]) if kind==12 else 0x7f812345+i)
  source=b.array(kind,values);root=b.structure([(9,12,source),(10,1,99)])
  case([call(0x478b00,root,[9,source])],b=b,label='owned array copy before replacing its source member')
# Formatter preserves literal bytes, marker parsing and original sprintf %% gaps.
formats=[b'',b'plain',b'\\x1',b'\\t',b'\\kX',b'\\t1',b'\\k1',b'\\t12/\\k10',b'\\t100',b'prefix \\k2 middle \\t3 suffix',b'\\t\xff',b'\\t1\\k1',b'%literal']
for source in formats:
 for size in [1,16]:
  b=Build();keys=b.array(3,[b.text(b'K%d'%(i+1)) for i in range(size)]);tricks=b.array(3,[b.text([b'Trick',b'80%%',b''][i%3]) for i in range(size)]);text=b.text(source)
  case([call(0x554890,args=[text,OUTPUT,keys,tricks,0]),call(0x554890,args=[text,OUTPUT+0x400,keys,tricks,512])],b=b,label='marker expansion and ignored capacity with real CRT sprintf')
for source in [b'\\k0',b'\\t00',b'\\k99',b'\\t01']:
 b=Build();keys=b.array(3,[b.text(b'%%key')]);tricks=b.array(3,[b.text(b'trick%%')]);text=b.text(source)
 case([call(0x554890,args=[text,OUTPUT,keys,tricks,0xffffffff])],b=b,label='single-item array ignores marker index and percent emits once')
# Shared actual environment for complete binding resolution and text parent.
def environment(kinds):
 b=Build();mapping=[];labels=[];bindings=[];combos=[];specials=[]
 for i,kind in enumerate(kinds):
  combo=0xa000+i;trick=0xb000+i;combos.append(combo)
  labels.append((combo,3,b.text(('Button%d'%i).encode())))
  trick_text=b.text(('Trick%d'%i).encode());trick_params=b.structure([(0xa1dc81f9,3,trick_text)])
  b.symbol(trick,10,b.structure([(0x7031f10c,10,trick_params)]))
  specials.append(b.structure([(0xa1dc81f9,3,b.text(('Special%d'%i).encode()))]))
  if kind=='integer':
   mapping.append((combo,1,i));entry=b.alloc(struct.pack('<II',0,trick_params));b.extra.append(patch(BODY+0x17c+i*4,'<I',entry))
  elif kind=='checksum':mapping.append((combo,13,trick))
  elif kind=='fallback':bindings.append(b.structure([(0x5b077ce1,13,trick),(0xa92a2280,13,combo),(0xb56a8816,1,1)]))
 b.symbol(0x8856c817,10,b.structure(labels));b.symbol(0xffd7913f,12,b.array(10,specials))
 root=b.structure([(0xd544aa2d,10,b.structure(mapping)),(0xac9b9eda,1,len(bindings)),(0xddbee809,10,b.structure([(0,12,b.array(10,bindings))]))]);b.header(PROFILE+0x5c,root)
 return b,b.array(13,combos)
for kinds in [[],['integer'],['checksum'],['fallback'],['missing'],['integer','checksum','fallback'],['checksum','missing'],['fallback','fallback']]:
 for special in [-2,-1,0]:
  b,combos=environment(kinds);keys=b.array(3,[0]*len(kinds));tricks=b.array(3,[0]*len(kinds))
  case([call(0x555b50,args=[combos,keys,tricks,special])],b=b,label='complete key/trick tables integer checksum fallback and partial failure')
# The complete update backs up originals once, handles strings/arrays differently,
# survives repeat calls and cleans up both successful and partial failure arrays.
sources=[0x0c5d7e6b,0x4bc5229d,0x63981d6f,0xda441d9a,0x1b3b4dd8];saved=[0x01f238b1,0x89e9c617,0x988330d3,0xb0d7628f,0xe0206064]
for kinds in [['checksum'],['integer'],['fallback'],['checksum','fallback'],['checksum','missing']]:
 for main in ['none','string','array']:
  for backup in ['absent','present','wrongtype']:
   b,combos=environment(kinds);params=[(0x79704516,12,combos)]
   if main=='string':params.append((sources[0],3,b.text(b'Use \\k1 for \\t1')))
   elif main=='array':params.append((sources[0],12,b.array(3,[b.text(b'Use \\k1'),b.text(b'Try \\t1')])) )
   for i in range(1,5):params.append((sources[i],3,b.text(('Field%d: '%i).encode()+b'\\k1 \\t1')))
   if backup!='absent':
    for name in saved:params.append((name,3,b.text(b'Existing \\t1')) if backup=='present' else (name,1,77))
   root=b.structure(params)
   case([call(0x556a00),call(0x556a00)],b=b,p=[patch(OBJECT+0x1c,'<I',root)],label='full objective text string array saved originals repeats and failure cleanup')
for mode in ['no_combos','empty_combos','special']:
 b,combos=environment(['checksum'] if mode=='special' else []);params=[]
 if mode!='no_combos':params.append((0x79704516,12,combos))
 if mode=='special':params.extend([(0,13,0x8e6014f6),(0x0b502200,1,0),(sources[1],3,b.text(b'\\t1'))])
 else:params.append((sources[1],3,b.text(b'no markers')))
 root=b.structure(params);case([call(0x556a00)],b=b,p=[patch(OBJECT+0x1c,'<I',root)],label='missing empty and special-combo objective paths')
scope='Fifteen original functions recover complete objective text update556a00, binding table construction555b50, marker formatter554890, profile/current/index/parameter/binding access and legacy QB/owned-array helpers. Actual original QB, symbol, profile, string-copy, array ownership and CRT sprintf paths execute; only allocator and Windows TLS/last-error services are adapted. Three undefined bytes9..11 per externally returned binding record are zeroed; checksums and flag are exact. Valid required profile/string fields, local skaters for integer bindings, mapped indices, successful allocation and fitting buffers retain original contracts. Replacement formats are argument-free literals/%%; conversions needing absent varargs are undefined in the original and outside the contract. Original ignored capacity, format-length advancement and scalar-main-text retention are preserved. No native gameplay callback substitution. Activation/state integration and a playable level remain unfinished.'
fixture={'base':BASE,'memory':'objective-text-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'objective-text-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),'padding bytes',undefined_padding,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_text_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'os_calls':dict(os_calls),'undefined_binding_padding_bytes_zeroed':undefined_padding,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
