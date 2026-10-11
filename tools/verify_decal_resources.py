"""Original D3DX math, material ownership/sorting and decal allocation."""
import hashlib,itertools,json,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
from decal_math_fixtures import build_math

out=ROOT/'local/validation/collision';report_path=out.parent/'decal-resources.json'
report_path.unlink(missing_ok=True)
math,math_path,math_oracle=build_math(out)
BASE,SIZE=0x1800000,0x80000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
TABLE,GROUPS,MATERIALS,SENTINELS,MESHES,NODES,ENTRIES,SORT=[BASE+x for x in [0x1000,0x2000,0x4000,0xe000,0x10000,0x12000,0x13000,0x14000]]
BUFFERS,DICTIONARY,BUCKETS,LINKS,LOG,HEAP=[BASE+x for x in [0x18000,0x29000,0x29100,0x29200,0x30000,0x40000]]
# Thread state is test-owned storage in an otherwise unused image region.
# Only the external CRT TLS accessor is replaced; rand itself executes intact.
TLS=0x7d2100
memory=bytearray(b'\xad'*SIZE);rng=random.Random(0x4ce9f0)
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,v):return [at,bytes(v).hex()]
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
def group(i):return GROUPS+i*32
def material(i):return MATERIALS+i*0x120
def sentinel(i,k):return SENTINELS+(i*3+k)*20
def mesh(i):return MESHES+i*0x100
def node(i):return NODES+i*20
def entry(i):return ENTRIES+i*8
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
put(TABLE,'<I',0)
for i in range(128):
 put(group(i),'<5I',0x40,material(i),*[sentinel(i,k) for k in range(3)])
 put(material(i)+8,'<I',1);put(material(i)+0x1c,'<I',bits(i%9-4))
 for k in range(3):
  p=sentinel(i,k);put(p,'<5I',0x64a898,0xffffffff,0,p,p)
for i in range(16):
 put(mesh(i)+0x14,'<I',material(i));put(mesh(i)+0x4c,'<I',ENTRIES+0x300+i*4)
 put(ENTRIES+0x300+i*4,'<I',i%3)
for i in range(64):
 put(node(i),'<5I',0x64a894,entry(i),i,node(i),node(i));put(entry(i),'<2I',i%3,mesh(i%16))
for i in range(2):
 b=BUFFERS+i*0x7c10;put(b+0x1c0c,'<I',material(i));put(material(i)+0x30,'<I',0x11223344+i)
put(DICTIONARY,'<6I',2,BUCKETS,0,0,0,0)
for i in range(4):put(BUCKETS+i*12,'<3I',0,0,0)
put(LINKS,'<6I',0,BUFFERS,LINKS+12,1,BUFFERS+0x7c10,0)
initial=bytes(memory)
globals_=[['thug_decal_buffers',0x7004b0,4],['thug_crt_random_state',TLS+0x14,4],['thug_lookup_node_pool',0x7d1808,4]]
defaults=[DICTIONARY,1,0]
functions={}
def bind(at,name,n=0,result='void',this=True,heap=False):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':n*4 if this else 0,'memory':heap}
bind(0x4ce960,'thug_material_node_delete',1,'word',heap=True)
bind(0x4ce9a0,'thug_material_sentinel_delete',1,'word',heap=True)
bind(0x4ce9d0,'thug_material_sentinel_destroy')
bind(0x4ceb30,'thug_material_group_initialize',1,'word',heap=True)
bind(0x4ce1d0,'thug_material_group_add_mesh',1,heap=True)
bind(0x4ce250,'thug_material_group_remove_mesh',1,heap=True)
bind(0x4cda60,'thug_material_table_find',1,'word')
bind(0x4cd9d0,'thug_material_group_compare',2,'word',False)
bind(0x4ce9f0,'thug_material_table_remove_mesh',1,heap=True)
bind(0x6242a0,'thug_crt_qsort',4,this=False)
functions['0x6242a0']['pointer_args']=[3]
bind(0x624230,'thug_crt_shortsort',4,this=False)
functions['0x624230'].update(stack_args=[0,2,3],register_args={'eax':1},pointer_args=[3])
bind(0x623ba3,'thug_crt_random',result='word',this=False)
bind(0x4b9a60,'thug_decal_find_or_create',1,'word',False,True)
exports=[[0x64a894,'thug_material_node_methods'],[0x64a898,'thug_material_sentinel_methods']]
pe=load()
for (at,_),fn in zip(exports,[0x4ce960,0x4ce9a0]):assert int.from_bytes(pe.get_data(at-0x400000,4),'little')==fn
pointer_fields={at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in dict(exports)}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[int(k,16) for k in functions]+[0x401cc0,0x588190,0x462740,0x4d1a90],event_limit=(HEAP-LOG)//48)
def tls(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);cpu.reg_write(UC_X86_REG_EAX,TLS)
 cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,tls,begin=0x629be5,end=0x629be5)
labels=[]
def call(fn,this=0,args=()):return fn,this,[v&0xffffffff for v in args]
def case(calls,p=(),changes=None,label='material resources'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,p,changes);labels.append(label)
 for at,data in p:
  b=bytes.fromhex(data)
  for i in range(0,len(b)-3,4):
   if int.from_bytes(b[i:i+4],'little') in dict(exports):pointer_fields.add(at+i)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):pointer_fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 return stages
def chain(i,k,indices):
 s=sentinel(i,k)
 p=[patch(s,'<5I',0x64a898,0xffffffff,0,node(indices[-1]) if indices else s,node(indices[0]) if indices else s)]
 for j,n in enumerate(indices):
  p.append(patch(node(n),'<5I',0x64a894,entry(n),0,node(indices[j-1]) if j else s,node(indices[j+1]) if j+1<len(indices) else s))
 return p
# Destructors preserve actual virtual-table identity and unlink ordering.
for fn in [0x4ce960,0x4ce9a0,0x4ce9d0]:
 for n in range(3):
  for flags in [0,1,2,3,0x80000000,0xffffffff]:
   p=chain(0,0,[0,1,2])+[patch(CONTEXT+24,'<I',sentinel(0,0)+12)]
   case([call(fn,node(n),[] if fn==0x4ce9d0 else [flags])]*2,p,label='linked node removal, repeated destruction and release snapshots')
 for flags in [0,1,0xffffffff]:
  case([call(fn,sentinel(0,0),[] if fn==0x4ce9d0 else [flags])],label='self-linked sentinel destruction')
for passes in [0,1,2,3,0x7fffffff,0xfffffffe,0xffffffff]:
 case([call(0x4ceb30,group(0),[material(0)])],[patch(material(0)+8,'<I',passes)],label='constructor allocation order and wrapping pass flags')
# Complete group construction, insert, reverse-first removal and idempotence.
for count in [0,1,2,3,8,16]:
 for selector in range(3):
  p=[patch(ENTRIES+0x300+i*4,'<I',(i+selector)%3) for i in range(16)]
  calls=[call(0x4ceb30,group(0),[material(0)])]
  calls += [call(0x4ce1d0,group(0),[mesh(i%4)]) for i in range(count)]
  calls += [call(0x4ce250,group(0),[mesh(i%4)]) for i in range(count+4)]
  case(calls,p,label='constructed lists with duplicate meshes and missing removals')
for count in [-1,0,1,2,8,16,64]:
 for wanted in [0,1,7,63,127]:
  p=[patch(TABLE,'<I',count&0xffffffff),patch(TABLE+4,'<'+'I'*max(count,0),*[group(i) for i in range(max(count,0))])]
  case([call(0x4cda60,TABLE,[material(wanted)])],p,label='signed table count, ordered identity and misses')
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for a,b in itertools.product([None,'missing',*special],repeat=2):
 p=[patch(SORT,'<2I',0 if a is None else group(0),0 if b is None else group(1))]
 for i,v in enumerate([a,b]):
  if v=='missing':p.append(patch(group(i)+4,'<I',0))
  elif v is not None:p.append(patch(material(i)+0x1c,'<I',v))
 case([call(0x4cd9d0,args=[SORT,SORT+4])],p,label='null/missing material, ordered priorities and unordered comparisons')
for count in [0,1,2,3,7,8,9,10,16,31,32,65,128,257]:
 for width in [4,5,8,12,17,32]:
  for mode in range(6):
   values=[i%128 for i in range(count)]
   if mode==1:values.reverse()
   if mode==2:rng.shuffle(values)
   if mode==3:values=[0]*count
   if mode==4:values=[None if i%3 else i%128 for i in range(count)]
   if mode==5:values=[rng.randrange(len(special)) for i in range(count)]
   data=b''.join(struct.pack('<I',0 if i is None else group(i))+bytes(rng.getrandbits(8) for _ in range(width-4)) for i in values)
   p=[raw(SORT,data)]
   if mode==5:p += [patch(material(i)+0x1c,'<I',special[i]) for i in range(len(special))]
   case([call(0x6242a0,args=[SORT,count,width,0x4cd9d0])],p,label='quicksort widths, threshold, equal identities, nulls and unordered priorities')
   if 1<=count<=10:case([call(0x624230,args=[SORT,SORT+(count-1)*width,width,0x4cd9d0])],p,label='private shortsort ABI and byte-preserving unstable ties')
case([call(0x6242a0,args=[0,0,0,0]),call(0x6242a0,args=[0,1,4,0]),call(0x6242a0,args=[0,10,0,0])],label='early-return count/width guards')
# Parent removal invokes genuine concrete node/sentinel destructors and CRT sort.
for count in [1,2,7,8,9,16,65]:
 for victim in sorted({0,count//2,count-1}):
  for remaining in [False,True]:
   p=[patch(TABLE,'<I',count),patch(TABLE+4,'<'+'I'*count,*[group(i) for i in range(count)]),patch(mesh(0)+0x14,'<I',material(victim))]
   p+=chain(victim,1,[0,1] if remaining else [0]);p += [patch(entry(0),'<2I',1,mesh(0)),patch(entry(1),'<2I',1,mesh(1))]
   case([call(0x4ce9f0,TABLE,[mesh(0)])]*2,p,label='table removal through real destructors, survivors, empty-group sort and repeat')
case([call(0x4ce9f0,TABLE,[mesh(0)])],[patch(mesh(0)+0x14,'<I',0)],label='unbound mesh early return')
case([call(0x4ce9f0,TABLE,[mesh(0)])],label='empty table lookup return')
for seed in [0,1,0xffffffff,0x80000000,0x7fffffff,*[rng.getrandbits(32) for _ in range(64)]]:
 case([call(0x623ba3)]*16,changes={1:seed},label='CRT recurrence, wrap, output mask and state sequence')
# Lookups cover inline/overflow, first-match reuse and null-value termination.
for mode in range(6):
 for texture in [0,0x11223344,0x11223345,0xffffffff]:
  p=[]
  if mode==1:p=[patch(BUCKETS,'<3I',0,BUFFERS,0)]
  if mode==2:p=[patch(BUCKETS,'<3I',0,0,LINKS)]
  if mode==3:p=[patch(BUCKETS,'<3I',0,BUFFERS,LINKS+12)]
  if mode==4:p=[patch(BUCKETS,'<3I',0,0,LINKS),patch(LINKS+4,'<I',0)]
  if mode==5:p=[patch(BUCKETS,'<3I',0,BUFFERS,LINKS+12),patch(material(1)+0x30,'<I',0x11223344)]
  case([call(0x4b9a60,args=[texture])]*2,p,changes={1:rng.getrandbits(32)},label='buffer reuse/create, table iteration, collisions and preserved bytes')
case([call(0x4b9a60,args=[i]) for i in [0,1,2,1,0,2,3]],label='sequential distinct textures, collisions and repeated reuse')

scope='Thirteen complete material/runtime routines: concrete list destructors, three-list group construction, insert/remove, table lookup/removal, material comparison, exact CRT quicksort/shortsort, CRT rand and decal material/buffer find-or-create. Complete parent sequences execute original game helpers, compare all arena/global bytes, allocation/release snapshots, sort tie order and pointer results. Only preinitialized game heap services and CRT TLS access are host boundaries; Windows memory-manager/TLS startup and allocation failure paths are outside this successful-allocation scope. No original GPU mesh destruction, complete projection, renderer or playable level is established.'
fixture={'base':BASE,'memory':'decal-resources-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(pointer_fields),
 'function_exports':[[0x4cd9d0,'thug_material_group_compare']],
 'memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope']}
fixture_path=out/'decal-resources-fixtures.json';fixture_path.write_text(json.dumps(fixture,separators=(',',':')))
(out/fixture['memory']).write_bytes(initial)
print('Original decal resources:',len(labels),sum(oracle.counts.values()),dict(oracle.coverage),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_decal_resources_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'math_counts':dict(math_oracle.counts),'math_callee_coverage':dict(math_oracle.coverage),
 'resource_counts':dict(oracle.counts),'resource_callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),
 'scope':math['scope']+' '+scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [fixture_path,math_path,out/fixture['memory'],out/math['memory'],out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS decal resources',flush=True)
