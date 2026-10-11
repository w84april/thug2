"""Moving-contact transport through original reference, matrix and timer callees."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'moving-contact.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x20000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
BODY,CONTACT,GATE,POINT,MATRIX,RIGHT,OUTPUT,REFS,LOG,HEAP=[BASE+x for x in [0x1000,0x2000,0x3000,0x4000,0x5000,0x5100,0x5200,0x6000,0x8000,0x10000]]
PHYSICS,STATE,SKATER=BASE+0xa000,BASE+0xc000,BASE+0xc100
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,GATE+0x18,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(BODY+4,'<I',0);put(BODY+0x4c,'<4f',10,20,30,1);put(BODY+0x6c,'<16f',*identity)
put(CONTACT,'<3I',0,0,0);put(CONTACT+0xc,'<16f',*identity);put(CONTACT+0x4c,'<4f',10,20,30,1)
put(GATE+0x18,'<I',0);put(POINT,'<4f',20,25,35,1)
put(MATRIX,'<16f',*identity);put(RIGHT,'<16f',*identity)
put(PHYSICS+12,'<I',SKATER);put(PHYSICS+0x1528,'<2I',STATE,GATE);put(STATE+0x88,'<B',0)
put(SKATER+0xac,'<4f',100,200,300,1);put(BODY+0xac,'<4f',10,20,30,1)
put(BODY+0x304,'<I',0);put(BODY+0x34c,'<4f',-10,-20,-30,1);put(BODY+0x36c,'<16f',*identity)
put(PHYSICS+0x140,'<5I',0,0,0,0,0)
initial=bytes(memory)
globals_=[['thug_frame_counter',0x7d1ec8,4],['thug_frame_rate',0x684fd0,4],['thug_timer_origin',0x696d64,4],['thug_time_scale',0x67d7c0,4],['thug_timer_offset',0x696d60,4]]
defaults=[60,bits(60.),0,bits(1.),7]
functions={}
def bind(at,name,argc=0,result='void',heap=False):functions[hex(at)]={'name':name,'this':True,'result':result,'memory':heap,'cleanup':argc*4,'stack_args':list(range(argc))}
bind(0x416d80,'thug_matrix_equal',1,'byte')
bind(0x416df0,'thug_matrix_rigid_inverse')
bind(0x40af60,'thug_matrix_transform_vector',2,'word')
bind(0x416e70,'thug_moving_contact_initialize',1,'word')
bind(0x416f00,'thug_moving_contact_update',1,'byte')
bind(0x427c70,'thug_skater_moving_contact_release',heap=True)
bind(0x427cb0,'thug_skater_has_moving_contact',result='byte',heap=True)
bind(0x43a930,'thug_collision_probe_assign',1,'word')
bind(0x427cd0,'thug_skater_moving_contact_acquire',1,'byte',heap=True)
bind(0x5021d0,'thug_skater_adjust_moving_contact',heap=True)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[int(k,16) for k in functions]+[0x404090,0x4637c0,0x4637e0,0x416dd0,0x44ece0,0x5be970,0x5df4ac,0x4f8160,0x417210,0x417240])
oracle.setword(0x684fe4,0x5df4ac)
labels=[];outcomes=Counter()
def velocity_adjustment(cpu,address,size,user):outcomes['relative_velocity_adjustments']+=1
oracle.cpu.hook_add(UC_HOOK_CODE,velocity_adjustment,begin=0x5021f9,end=0x5021f9)
def call(fn,this,args=()):return (fn,this,list(args))
def case(calls,p=(),changes=None,label='contact',floats=(),quiet=()):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,p,changes);labels.append(label)
 for s in stages:
  s['float_fields']=list(floats);s['quiet_float_fields']=list(quiet)
  if s['fn']=='0x416f00':outcomes['live_updates' if s['result'] else 'missing_owner_updates']+=1
 if len(labels)%100==0:print('Original contact cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x416f00)
# Every matrix lane participates, ordered equality accepts signed zero and
# rejects even identical NaN payloads. Untouched bytes remain exact.
for lane in range(16):
 for value in [0,0x80000000,0x3f800000,0x40000000,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
  for same in [False,True]:
   p=[patch(MATRIX+lane*4,'<I',value)]
   if same:p.append(patch(RIGHT+lane*4,'<I',value))
   case([call(0x416d80,MATRIX,[RIGHT])],p,label='ordered sixteen-lane matrix equality')
for i in range(192):
 values=[rng.uniform(-100,100) for _ in range(16)]
 if i<96:values[i%16]=[0.,-0.,1e30,-1e30,1e-30,float('nan')][(i//16)%6]
 if i>=96:
  values=[rng.choice([0.,-0.,1e30,-1e30,1e-30,-1e-30,1.,float('inf')]) for _ in range(16)]
 p=[patch(MATRIX,'<16f',*values)]
 if i<16:p.append(patch(MATRIX+i*4,'<I',0x7f812345))
 case([call(0x416df0,MATRIX)],p,label='rigid inverse wide translation and asymmetric NaN swaps',
  floats=[MATRIX+j*4 for j in [12,13,14]],quiet=[MATRIX+j*4 for j in [4,8,9]])
# Snapshot semantics include output overlapping either the input vector or the
# matrix, while the exact accumulation order differs for X.
for i in range(224):
 matrix=[rng.uniform(-20,20) for _ in range(16)];point=[rng.uniform(-1e4,1e4) for _ in range(4)]
 if i>=112:
  values=[0.,-0.,1e30,-1e30,1e-30,-1e-30,1.,float('inf'),float('nan')]
  matrix=[rng.choice(values) for _ in range(16)];point=[rng.choice(values) for _ in range(4)]
 target=[OUTPUT,POINT,POINT+4,POINT-4,MATRIX,MATRIX+4,MATRIX+48][i%7]
 source=MATRIX+16 if i%9==0 else POINT
 case([call(0x40af60,MATRIX,[target,source])],[patch(MATRIX,'<16f',*matrix),patch(POINT,'<4f',*point)],
  label='homogeneous transform wide products and input output matrix aliases',floats=range(target,target+16,4))

def chain(order,owner=BODY):
 p=[patch(owner+4,'<I',order[0] if order else 0)]
 for i,at in enumerate(order):p.append(patch(at,'<3I',owner,order[i-1] if i else 0,order[i+1] if i+1<len(order) else 0))
 return p

# Constructors retain uninitialized rotation/padding and raw float words.
# Consecutive construction and releases exercise real reference-chain changes.
for i in range(48):
 order=[REFS+j*16 for j in range(i%4)];p=chain(order)
 p+=[patch(BODY+0x4c,'<4I',*([0x7f812345,0x80000000,0xff800000,0x3f800000] if i%3==0 else [bits(i*1.5),bits(i*-3.),0,0x3f800000])),patch(GATE+0x18,'<I',CONTACT)]
 if i%4==0:p.append(patch(BODY+0x6c+(i%16)*4,'<I',0x7f812345))
 calls=[call(0x416e70,CONTACT,[BODY]),call(0x416e70,CONTACT+0x100,[BODY]),call(0x427cb0,GATE),call(0x427c70,GATE),call(0x427c70,GATE)]
 case(calls,p,label='construct contacts link references and release one owner')

# Actual owner state differs from the contact's saved state. A second update
# tests the snapshot from the first; position may alias contact fields written
# before it is read, as the parent routine can supply shared state.
for i in range(256):
 angle=[0.,math.pi/2,-math.pi/2,math.pi,.23][i%5];c,s=math.cos(angle),math.sin(angle)
 current=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
 saved=identity[:];position=[10.,20.,30.,1.];old=[7.,18.,31.,1.]
 if i%7==0:old=position[:];current=saved[:]
 if i%11==0:current[i%16]=[float('nan'),float('inf'),-0.,1e30][(i//11)%4]
 if i%13==0:saved[(i+3)%16]=[float('nan'),-0.,1e-30,-1e30][(i//13)%4]
 if i>=192:
  values=[0.,-0.,1e30,-1e30,1e-30,1.,float('inf'),float('nan')]
  position=[rng.choice(values) for _ in range(4)];old=[rng.choice(values) for _ in range(4)]
 p=chain([REFS,CONTACT,REFS+16])+[patch(GATE+0x18,'<I',CONTACT),patch(BODY+0x4c,'<4f',*position),patch(BODY+0x6c,'<16f',*current),
   patch(CONTACT+0xc,'<16f',*saved),patch(CONTACT+0x4c,'<4f',*old)]
 at=[POINT,BODY+0x4c,CONTACT+0x4c,CONTACT+0x5c,CONTACT+0x6c,CONTACT+0x50,CONTACT+0x60][i%7]
 stages=case([call(0x416f00,CONTACT,[at]),call(0x416f00,CONTACT,[at])],p,
  label='translate rotate repeat and aliased point transport',floats=range(CONTACT+0x5c,CONTACT+0xac,4))
 outcomes['final_rotation_changed']+=oracle.cpu.mem_read(CONTACT+0xac,1)[0]!=0

# Detached, dead-owner and head/middle/tail contacts, with raw links retained
# when no owner exists. Release is idempotent, and time wraps as uint32.
for i in range(96):
 variant=i%6
 orders=[[],[CONTACT],[CONTACT,REFS,REFS+16],[REFS,CONTACT,REFS+16],[REFS,REFS+16,CONTACT],[]]
 p=chain(orders[variant])+[patch(GATE+0x18,'<I',CONTACT if variant else 0)]
 if variant==5:p.append(patch(CONTACT,'<3I',0,REFS,REFS+16))
 p.append(patch(CONTEXT+24,'<I',GATE+[0x18,0x6c,0x70][i%3]))
 changes={0:[0,1,2**24+1,2**31,0xffffffff][i%5],1:bits([30.,60.,59.94,144.][i%4]),2:[0,0xffffffff,17][i%3],3:bits([1.,-1.,.125,1e12,float('nan')][i%5]),4:[0,0xffffffff,12345][i%3]}
 calls=([call(0x416f00,CONTACT,[POINT])] if variant in [0,5] else [])+[call(0x427cb0,GATE),call(0x427c70,GATE),call(0x427cb0,GATE)]
 case(calls,p,changes,label='contact ownership release timer and missing owner')
# Floor/contact handling copies the current probe into its saved probe. Exercise
# real intrusive ownership changes, same-owner chains and self-assignment.
PROBE,OTHER=BASE+0x7000,BASE+0x7100
for i in range(96):
 source=PROBE if i%6==0 else OTHER
 p=[[PROBE,bytes(rng.randrange(256) for _ in range(0xb0)).hex()],
    [OTHER,bytes(rng.randrange(256) for _ in range(0xb0)).hex()],
    patch(PROBE+0x98,'<3I',0,0,0),patch(OTHER+0x98,'<3I',0,0,0),patch(BODY+0x304,'<I',0)]
 order=[REFS]
 if i%2:order.append(PROBE+0x98)
 if i%3:order.append(OTHER+0x98)
 order.append(REFS+16)
 p+=chain(order)
 if i%4==0:
  # A separate live owner for the source, after removing it from the first list.
  order=[at for at in order if at!=OTHER+0x98];p+=chain(order)
  p+=[patch(BODY+0x304,'<I',OTHER+0x98),patch(OTHER+0x98,'<3I',BODY+0x300,0,0)]
 case([call(0x43a930,PROBE,[source]),call(0x43a930,PROBE,[source])],p,
  label='saved collision probe ownership transfer padding and self assignment')
# Acquire contacts from a real probe reference and run the enclosing physics
# wrapper. Repeat to ensure velocity is adjusted only on a new attachment.
for i in range(192):
 variant=i%6;probe=PHYSICS+0xa8;ref=probe+0x98
 order=[REFS,REFS+16];other_order=[]
 if variant in [1,2,3,4]:order.insert(1,ref)
 if variant in [2,5]:order.insert(1,CONTACT)
 if variant==3:other_order=[CONTACT]
 p=chain(order)+chain(other_order,BODY+0x300)+[patch(GATE+0x18,'<I',CONTACT if variant>=2 else 0)]
 if variant==4:p.append(patch(CONTACT,'<3I',0,0,0))
 p+=[patch(probe+0xa4,'<I',[0,1,0xffffffff][i%3]),patch(STATE+0x88,'<B',[0,1,255,0][(i//6)%4]),
     patch(SKATER+0xac,'<4f',*[rng.uniform(-1000,1000) for _ in range(4)])]
 if i%11==0:p.append(patch(BODY+0xac+(i%4)*4,'<I',0x7fc12345))
 calls=([call(0x427cd0,GATE,[probe])]*2 if (i//24)%2 else [call(0x5021d0,PHYSICS)]*2)+[call(0x427c70,GATE)]
 stages=case(calls,p,label='probe acquisition changed owner suppression and one-time relative velocity',floats=range(SKATER+0xac,SKATER+0xbc,4))
 outcomes['new_contacts']+=sum(s['result']==1 for s in stages if s['fn']=='0x427cd0')
assert outcomes['live_updates'] and outcomes['missing_owner_updates'] and outcomes['relative_velocity_adjustments'] and oracle.coverage['0x5df4ac']
scope='Complete original moving-contact construction, translation/rotation transport, release, validity query, probe-driven acquisition and skater relative-velocity adjustment, with matrix equality, rigid inverse, homogeneous vector transform and saved collision-probe assignment. Real reference-list, result-copy, matrix multiply and timer callees run; full arena, globals and heap observations compare, including self-assignment, preserved padding, owner replacement and repeated acquisition. Arithmetic NaNs compare only at typed outputs; three inverse swap destinations explicitly quiet signaling NaNs per x87. The original D3DX SSE backend is selected and allocations succeed. OS CPU selection, physical x87 exception state, frame-counter producer, complete skating updates and playable-level integration remain outside this check.'
fixture={'base':BASE,'memory':'moving-contact-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'moving-contact-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete',len(labels),'cases',dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_moving_contact_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',dict(oracle.counts))
