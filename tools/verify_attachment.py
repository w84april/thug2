"""Original attachment movement with real node provider, math, QB and events."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
import verify_wall_response as w
from specimen import ROOT,SHA256
out=w.out;report_path=out.parent/'attachment.json';report_path.unlink(missing_ok=True)
prior=w.prior;BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
P,BODY,BODY2,STATE,STATE2,INPUT,CALLBACK=w.P,w.BODY,w.BODY2,w.STATE,w.STATE2,w.INPUT,w.CALLBACK
OWNER,COMPONENT,PROVIDER,GATE,CONTACT,POINTS,NODES,VECTORS,GRAPH=0x1956000,0x1956400,0x1956500,0x1956600,0x1956700,0x1956900,0x1957000,0x1958000,0x1960000
QUERY,OUTPUT,MATRIX=VECTORS,VECTORS+0x100,VECTORS+0x200
patch=w.patch;bits=w.bits
identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def number(n):return struct.unpack('<f',struct.pack('<I',n))[0]
put(P+4,'<I',0x5bd63b29);put(P+16,'<I',0);put(P+0x2ed,'<B',0);put(P+0x302,'<B',0);put(P+0x152c,'<I',GATE)
put(P+0x24a,'<B',0);put(P+0x24c,'<if',0,0);put(P+0x8c,'<f',1/60)
put(GATE+0x18,'<I',CONTACT);put(CONTACT,'<3I',OWNER,0,0);put(CONTACT+0x5c,'<4f',0,0,0,0)
put(COMPONENT,'<8I',0,0x3506ce64,0,OWNER,0,0,0,PROVIDER)
put(PROVIDER,'<I',0x6462d4);put(PROVIDER+0x18,'<I',POINTS);put(POINTS,'<IB3s',NODES,0,b'abc')
put(OWNER+0x100,'<I',COMPONENT);put(OWNER+0x4c,'<4f',0,0,0,1);put(OWNER+0x6c,'<16f',*identity);put(OWNER+0xc0,'<16f',*identity)
for state in [STATE,STATE2]:put(state+0x88,'<B',1)
for body in [BODY,BODY2]:
 put(body+0xbc,'<B',0);put(body+0x100,'<I',P);put(body+0x4c,'<4f',0,0,-10,1);put(body+0x6c,'<16f',*identity)
for at in [0xb0,0xd0,0x110,0x130]:put(INPUT+at,'<B',0)
put(MATRIX,'<16f',*identity);put(QUERY,'<4f',0,0,0,1)
for i in range(4):put(NODES+i*0x20,'<4fI',i*24,0,0,1,NODES+(i+1)*0x20 if i<3 else 0)
initial=bytes(memory);oracle=w.oracle;cpu=w.cpu
oracle.base=BASE;oracle.initial=initial;globals_=prior['globals'];defaults=prior['cases'][0]['globals'][:];gindex={g[1]:i for i,g in enumerate(globals_)}
oracle.globals=globals_;oracle.defaults=defaults
functions=w.functions;functions.clear()
def bind(at,name,argc=0,result='void',heap=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'stack_args':list(range(argc)),'memory':heap}
 cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
bind(0x4023a0,'thug_vector_length_squared',result='double')
bind(0x402440,'thug_vector_sum',3,'word',this=False)
bind(0x46b7e0,'thug_input_button_clear_latch')
bind(0x5480f0,'thug_attachment_provider_points',result='word')
bind(0x469340,'thug_attachment_set_transform',1)
bind(0x469350,'thug_attachment_point_position',2)
bind(0x51ba70,'thug_attachment_nearest',2,'word')
bind(0x51bc70,'thug_attachment_indexed',2,'byte')
bind(0x501db0,'thug_skater_update_attachment',heap=True)
for at in [0x45db90,0x406080,0x40af60,0x478f00,0x580400,0x4750b0,0x475750,0x462f00]:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
fields=set(prior['pointer_fields'])|{PROVIDER};exports=prior['pointer_exports']+[[0x6462d4,'thug_attachment_provider_methods']]
known={entry[0] for entry in exports}|{w.NATIVE,w.RECEIVE,w.OBJECT}
labels=[];outcomes=Counter()
branches={0x501eb0:'candidate_searches',0x501f7b:'changed_index',0x502138:'incremental_motion',0x50210e:'arrived',0x502161:'direct_position',0x502182:'orientation_copy',0x5020e4:'distance_rejected',0x5021ab:'missing_contact',0x51bd17:'indexed_found',0x51bd64:'indexed_success',0x51bbdc:'nearest_candidate_accepted'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={}
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));return at
 def symbol(self,key,kind,value):
  bucket=w.BUCKETS+(key&4095)*4;previous=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0]);at=self.alloc(struct.pack('<BBHIIII',0,kind,0,key,0,value,previous));self.buckets[bucket]=at
 def numeric(self,key,value):self.symbol(key,1 if isinstance(value,int) else 2,value&0xffffffff if isinstance(value,int) else bits(value))
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(at,'<I',v) for at,v in self.buckets.items()]
def settings(separation=10.,rate=120.,local=False):
 b=Build();entries=[(0x97496256,1 if isinstance(rate,int) else 2,rate&0xffffffff if isinstance(rate,int) else bits(rate))] if local else []
 nodes=[b.alloc(struct.pack('<BBHIII',kind*2,0,0,key,value,0)) for key,kind,value in entries]
 params=b.alloc(struct.pack('<II',0,nodes[0] if nodes else 0));b.symbol(0x8cbc89dd,10,params);b.symbol(0xd3d12913,10,params)
 b.numeric(0x21fb182c,separation);b.numeric(0x97496256,rate);return b

def call(fn,this=0,args=()):return fn,this,list(args)+([w.PRINT] if functions[hex(fn)]['memory'] else [])
def case(calls,p=(),b=None,label='attachment',floats=(),quiet=()):
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,(b or settings()).patches()+list(p));labels.append(label);callbacks=0
 for s in stages:
  s['float_fields']=list(floats);s['quiet_float_fields']=list(quiet);merged=[]
  for at,data in s['outputs']:
   if at==CALLBACK:
    count=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=count-callbacks;callbacks=count
   if int.from_bytes(bytes.fromhex(data),'little') in known:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged;outcomes['callbacks']+=s['callbacks']
 if len(labels)%100==0:print('Original attachment cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x501db0)
special=[0,0x80000000,1,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffa12345,bits(1),bits(-1),bits(1e-30),bits(1e30)]
for i in range(96):
 values=[rng.choice(special) if i<32 else rng.randrange(2**32) for _ in range(16)]
 p=[patch(VECTORS,'<16I',*values)]
 case([call(0x4023a0,VECTORS)],p,label='squared length exponent range and nonfinite inputs')
 target=VECTORS+[0,4,12,16,32][i%5]
 case([call(0x402440,args=[target,VECTORS,VECTORS+16])],p,label='four lane sum snapshots overlap',floats=range(target,target+16,4))
for value in [0,1,255]:case([call(0x46b7e0,INPUT+0xa0)]*2,[patch(INPUT+0xb0,'<I',0xabcdef00|value)],label='one byte latch clear')
for pointer in [0,POINTS,NODES]:case([call(0x5480f0,PROVIDER)],[patch(PROVIDER+0x18,'<I',pointer)],label='concrete provider method')
for offset in [0,4,8,12,16,32]:
 case([call(0x469340,POINTS,[POINTS+offset])],[[POINTS,bytes(rng.randrange(256) for _ in range(96)).hex()]],label='flag before overlapping raw matrix copy')
for i in range(128):
 values=[rng.choice(special) if i<64 else bits(rng.uniform(-100,100)) for _ in range(16)]
 matrix=[rng.uniform(-4,4) for _ in range(16)]
 target=VECTORS+[0,4,12,16,32][i%5];active=i%2
 p=[patch(POINTS+4,'<B',active),patch(POINTS+8,'<16f',*matrix),patch(VECTORS,'<16I',*values)]
 case([call(0x469350,POINTS,[target,VECTORS])],p,label='raw versus transformed point and overlaps',floats=range(target,target+16,4) if active else [])
# Null gates leave outputs untouched; empty/missing indices retain AL1 and also
# leave the indexed output untouched. Nearest empty lists write their default.
for gate in ['valid','no body','no provider','no points','empty']:
 p=[]
 if gate=='no body':p=[patch(COMPONENT+12,'<I',0)]
 if gate=='no provider':p=[patch(COMPONENT+0x1c,'<I',0)]
 if gate=='no points':p=[patch(PROVIDER+0x18,'<I',0)]
 if gate=='empty':p=[patch(POINTS,'<I',0)]
 for index in [-1,0,1,3,4,0x7fffffff]:
  case([call(0x51ba70,COMPONENT,[OUTPUT,QUERY]),call(0x51bc70,COMPONENT,[OUTPUT,index&0xffffffff])],p,label='provider gates and missing indexed outputs',floats=range(OUTPUT,OUTPUT+16,4))
for i in range(192):
 count=i%8;angle=rng.uniform(-math.pi,math.pi);c,s=math.cos(angle),math.sin(angle)
 orientation=[c,0,-s,0,0,1,0,0,s,0,c,0,11,22,33,1]
 if i>=128:orientation=[rng.choice([0.,-0.,1.,1e30,1e-30,float('inf'),float('nan')]) for _ in range(16)]
 p=[patch(OWNER+0x6c,'<16f',*orientation),patch(OWNER+0x4c,'<4f',*[rng.uniform(-100,100) for _ in range(3)],1),patch(POINTS,'<I',NODES if count else 0),patch(QUERY,'<4f',*[rng.uniform(-200,200) for _ in range(3)],1)]
 for j in range(count):p.append(patch(NODES+j*0x20,'<4fI',*[rng.uniform(-100,100) for _ in range(3)],1,NODES+(j+1)*0x20 if j+1<count else 0))
 target=[OUTPUT,QUERY,OWNER+0x4c,OWNER+0x6c,POINTS+8,NODES][i%6]
 case([call(0x51ba70,COMPONENT,[target,QUERY])],p,label='nearest projected nodes transformed body and output aliases',floats=range(target,target+16,4))
 case([call(0x51bc70,COMPONENT,[target,i%10])],p,label='indexed projected nodes and output aliases',floats=range(target,target+16,4) if i%10<count else [])
# Strict nearest ties preserve the first node, including distance just at the
# initial finite sentinel. Query/body data can include wide-exponent values.
for x in [0.,1.,-1.,1e7,1e14,1e30,float('nan'),float('inf')]:
 p=[patch(NODES,'<4fI',x,0,0,1,NODES+32),patch(NODES+32,'<4fI',-x,0,0,1,0)]
 case([call(0x51ba70,COMPONENT,[OUTPUT,QUERY])],p,label='nearest strict tie threshold and unordered candidates',floats=range(OUTPUT,OUTPUT+16,4))
position_fields=[body+j for body in [BODY,BODY2] for j in range(0x4c,0x5c,4)]
def parent(p=(),b=None,label='complete attachment',repeat=1):return case([call(0x501db0,P)]*repeat,p,b,label,position_fields)
for which in [0,1]:
 parent([patch(GATE+0x18 if which==0 else CONTACT,'<I',0)],label='missing contact or owner event',repeat=2)
for mask in range(16):
 for moving in [0,1]:
  p=[patch(INPUT+at,'<B',255 if mask&(1<<j) else 0) for j,at in enumerate([0xb0,0x110,0xd0,0x130])]
  p += [patch(P+0x24a,'<B',moving),patch(P+0x250,'<f',1)]
  parent(p,label='input latch precedence search and repeated movement',repeat=3)
for i in range(160):
 index=i%4;position=[rng.uniform(-180,180),rng.uniform(-20,20),rng.uniform(-100,100),1]
 p=[patch(P+0x24a,'<B',i%2),patch(P+0x24c,'<I',index),patch(BODY+0x4c,'<4f',*position),patch(CONTACT+0x5c,'<4f',*[rng.uniform(-2,2) for _ in range(3)],0),patch(P+0x8c,'<f',[0.,1/60,-1/60,.5,1e-30][i%5])]
 b=settings(separation=[0.,-0.,10.,-10.,1e30,float('nan'),2**24+1,2**31-1][i%8],rate=[0.,120.,-120.,1e30,1e-30,float('nan'),2**24+1,-2**31][(i//8)%8],local=i%3==0)
 parent(p,b,label='snap approach escape wide parameters and displacement',repeat=2)
# Side search with no different index must exhaust all 19 candidate distances.
parent([patch(NODES+16,'<I',0),patch(INPUT+0xb0,'<B',1)],label='same node exhausts side search')
# Invalid selected-index behavior is checked on 51bc70 itself. Parent cases
# only proceed into geometry with a valid index; disabled movement still tests
# the changed -1 search result and its actual event without reading stack data.
for gate in ['state','no provider','no points']:
 p=[patch(STATE+0x88,'<B',0),patch(INPUT+0xb0,'<B',1)]
 if gate=='no provider':p.append(patch(COMPONENT+0x1c,'<I',0))
 if gate=='no points':p.append(patch(PROVIDER+0x18,'<I',0))
 parent(p,label='disabled geometry after search and failed provider')
# Actual event receiver and QB handlers can redirect the body or mutate the
# current contact after selection. The originally captured owner is retained.
for mode,at,value in [(1,STATE+0x88,0),(1,P+0x24a,0),(2,P+0x24c,2),(2,GATE+0x18,0),(3,0,BODY2),(4,0,STATE2),(2,CONTACT,0),(2,CONTACT+0x5c,bits(10))]:
 p=[patch(INPUT+0xb0,'<B',1),patch(BODY+0x4c,'<4f',20,0,-10,1),patch(CALLBACK+4,'<3I',mode,at,value)]
 parent(p,label='changed index event callback mutation',repeat=1)
for event in [0x74bf80cf,0x2e7474b5,0x47d44b84]:
 p=[patch(w.EM+0x14,'<I',w.RECEIVER),patch(0x1942400,'<I',event),patch(CALLBACK+4,'<3I',6,STATE+0x88,0)]
 if event==0x47d44b84:p.append(patch(GATE+0x18,'<I',0))
 else:p += [patch(INPUT+(0xb0 if event==0x74bf80cf else 0x130),'<B',1),patch(BODY+0x4c,'<4f',40,0,-10,1)]
 parent(p,label='selection and missing-contact events execute actual QB handler')
assert outcomes['candidate_searches'] and outcomes['incremental_motion'] and outcomes['direct_position'] and outcomes['arrived'] and outcomes['distance_rejected'] and outcomes['changed_index']
assert oracle.coverage['0x5480f0'] and oracle.coverage['0x4750b0'] and not w.callback_counts
scope='Nine original functions: complete moving attachment update 501db0; nearest/indexed projected points 51ba70/51bc70; point transform setup/query 469340/469350; concrete provider5480f0; latch clear46b7e0; snapshot sum402440 and squared length4023a0. Actual component lookup, virtual provider, transforms, projection, parameters, event/QB execution and heap callees run. Full arena/global bytes, events and heap effects compare. Missing indexed points retain original success-without-write behavior; enclosing movement tests use valid selected points whenever geometry executes because the original otherwise reads an unwritten stack local. Arithmetic NaNs compare only at declared derived outputs. Native commands and allocation remain instrumented boundaries; complete ground/floor, startup, rendering and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'attachment-memory.bin','memory_adapter':w.ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':prior['memory_exports'],'globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_command_callbacks','pointer_symbols':prior['pointer_symbols'],'pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],'native_callbacks':prior['native_callbacks']}
path=out/'attachment-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_attachment_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'rebound-callbacks.wasm',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
