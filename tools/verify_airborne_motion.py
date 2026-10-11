"""Compare ten airborne prerequisites against complete original instruction paths."""
from pathlib import Path
# Reuse the established live graph without running its grounded cases.
task_source=Path(__file__).with_name('verify_grounded_update.py').read_text()
exec(compile(task_source.split('\nfor speed in [0,100]:')[0].replace("'grounded-update.json'","'airborne-motion.json'"),'<airborne prerequisites>','exec'))
NEW=[(0x4061a0,'thug_vector_align_magnitude',1,'word',False,False,True),
 (0x4fc370,'thug_vector_clear_below',1,'word',False,False,True),
 (0x420250,'thug_time_since',1,'word',False,False,False),
 (0x4fc400,'thug_skater_moving_contact_age',0,'word',False,False,True),
 (0x4fc470,'thug_skater_set_material',1,'void',True,True,True),
 (0x404e70,'thug_matrix_rotation_z',2,'word',False,False,False),
 (0x405670,'thug_matrix_rotate_x',1,'word',False,False,True),
 (0x504910,'thug_skater_pitch_input',0,'void',False,False,True),
 (0x504a60,'thug_skater_transfer_orientation',0,'void',False,False,True),
 (0x504df0,'thug_skater_upright_orientation',0,'void',False,False,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
for at,args in [(0x4fc370,[0]),(0x404e70,[1]),(0x405670,[0])]:functions[hex(at)]['float_args']=args
for at in [0x404090,0x416df0,0x580790,0x46b920]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
air_branches={0x504940:'pitch_inputs',0x50497b:'pitch_positive',0x5049a1:'pitch_negative',0x504a04:'pitch_ramp',0x504a1e:'pitch_rotate',0x504a7a:'transfer_active',0x504a9f:'transfer_clamp',0x504aa7:'transfer_ease',0x504e12:'upright_test',0x504e55:'upright_positive',0x504e88:'upright_negative',0x504ea2:'upright_rotate'}
branch_at.update(air_branches)
for at in air_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
air_base_case=case
def case(calls,patches=(),changes=None,label='airborne',floats=()):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=air_base_case(calls,patches,changes,label)
 for s in stages:s['float_fields']=list(floats)
 return stages
rng=random.Random(0x504910)
vectors=[[0,0,0,1],[3,4,0,9],[-0.,0,-0.,-0.],[1e-40,-1e-40,1e-40,1],[1e30,-1e30,1e30,1],[math.inf,1,2,3],[math.nan,1,2,3]]
for scale in [1e-30,1e-10,1,1e10,1e30]:
 vectors += [[rng.uniform(-scale,scale) for _ in range(4)] for j in range(5)]
for i,v in enumerate(vectors):
 d=vectors[(i+3)%len(vectors)]
 for shift in [0,4,8,16]:
  case([call(0x4061a0,M0,[M0+shift])],[patch(M0,'<8f',*(v+d))],label='magnitude alignment overlapping inputs',floats=[M0+4*j for j in range(4)])
 for threshold in [0,1,5,-5,1e30,math.nan]:
  case([call(0x4fc370,M0,[bits(threshold)])],[patch(M0,'<4f',*v)],label='strict threshold clear or bit-preserving no-write')
case([call(0x4fc370,M0,[bits(1)])],[patch(M0,'<4I',0x7f800001,0xff800001,0x7fc12345,0x80000000)],label='unordered clear retains signaling payloads')
for timestamp in [0,1,1666,1667,0x7fffffff,0x80000000,0xffffffff]:
 for counter in [0,100,0xffffffff]:
  for offset in [0,0x80000000,0xffffffff]:
   case([call(0x420250,args=[timestamp]),call(0x4fc400,GROUND_GATE)],[patch(GROUND_GATE+0x70,'<I',timestamp)],{0x7d1ec8:counter,0x696d60:offset},label='timestamp and contact-age unsigned wrap')
for angle in [0,-0.,.01,-.01,math.pi,-math.pi/2,1e20,math.nan]:
 case([call(0x404e70,args=[MOUT,bits(angle)])],label='Z rotation returned pointer and all matrix lanes',floats=[MOUT+4*j for j in range(16)])
 for matrix in [identity,[float(j-8) for j in range(16)],[rng.uniform(-2,2) for j in range(16)]]:
  case([call(0x405670,M0,[bits(angle)])],[patch(M0,'<16f',*matrix)],label='X premultiplication uses original SSE backend',floats=[M0+4*j for j in range(16)])

def air_config(cutoff=100,endpoint=300,rate=2):
 b=grounded_config(numbers={0x5f70ef46:cutoff,0x12cd2d14:endpoint,0xabd57877:90})
 pair=b.alloc(struct.pack('<I2f',0,rate,rate));b.symbol(0xcbfdd841,10,b.structure([(0,5,pair)]))
 return b

def parent(at,p=(),b=None,before=(),changes=None,label='airborne parent',repeat=1,floats=()):
 b=b or air_config()
 return case(body_setup()+list(before)+[call(at,PHYS) for _ in range(repeat)],b.patches()+list(p),changes,label,floats)[-1]

for mask in range(4):
 for elapsed in [0,1,99,100,101,299,300,301,0x7fffffff,0x80000000,0xffffffff]:
  for dt in [0,1/60]:
   p=[patch(INPUT+0x20,'<B3xI',mask&1,(1666-elapsed)&0xffffffff),patch(INPUT+0x40,'<B3xI',mask>>1,(1666-elapsed)&0xffffffff),patch(PHYS+0x8c,'<f',dt),patch(PHYS+0x18,'<16f',*[-x for x in identity])]
   parent(0x504910,p=p,label=f'pitch buttons {mask} signed age {elapsed} dt {dt}')
for at in [SKATER_STATE+0x78,SKATER_STATE+0xc0,SKATER_STATE+0x30,INPUT+0x160,INPUT+0x180]:
 parent(0x504910,p=[patch(at,'<B',255),patch(INPUT+0x20,'<B',1)],label='pitch early state or input gate')
for cutoff,endpoint in [(0,0),(100,300),(300,300),(-100,100),(16777216,16777220)]:
 for elapsed in [0,100,300,16777215,16777216,16777217]:
  parent(0x504910,p=[patch(INPUT+0x20,'<B3xI',1,(1666-elapsed)&0xffffffff)],b=air_config(cutoff,endpoint),label='pitch endpoints and exact FILD cutoff')
# A held second button overrides the first timestamp as well as its rate.
parent(0x504910,p=[patch(INPUT+0x20,'<B3xI',1,1666),patch(INPUT+0x40,'<B3xI',1,1365)],label='second pitch input exceeds cutoff')

for active in [0,1,255]:
 for small in [0,1]:
  for progress,duration,dt in [(-.5,1,.01),(0,1,0),(0,1,1/60),(.49,1,.01),(.99,1,.01),(1,1,.1),(2,1,.1),(1,-1,.1),(1e30,1e30,1e30)]:
   target=identity[:];angle=.7;target[0]=target[10]=math.cos(angle);target[2]=-math.sin(angle);target[8]=math.sin(angle)
   p=[patch(SKATER_STATE+0x78,'<B',active),patch(PHYS+0x3f0,'<37fB',*(identity+target+[0,1,0,0,angle]),small),patch(PHYS+0x488,'<2f',progress,duration),patch(PHYS+0x8c,'<f',dt),patch(PHYS+0x4a0,'<16f',*identity)]
   parent(0x504a60,p=p,label=f'transfer orientation gate {active} interpolation {small} progress {progress}',repeat=4 if progress==0 and dt>0 else 1)
# Unlike a rounded increment, the retained x87 sum remains finite before divide.
p=[patch(SKATER_STATE+0x78,'<B',1),patch(PHYS+0x3f0,'<37fB',*(identity+identity+[0,1,0,0,0]),1),patch(PHYS+0x488,'<2f',3e38,3e38),patch(PHYS+0x8c,'<f',3e38),patch(PHYS+0x4a0,'<16f',*identity)]
parent(0x504a60,p=p,label='unspilled transfer progress exponent')
for fy in [-1,-.95,-.9499999,0,.9499999,.95,1,math.nan]:
 for correction in [-1,-.02,0,.02,1]:
  basis=identity[:];basis[4]=-correction;basis[9]=fy
  parent(0x504df0,p=[patch(BODIES+0x6c,'<16f',*basis)],label='upright orientation tilt and threshold',floats=[BODIES+0x6c+4*j for j in range(16)]+[PHYS+0x18+4*j for j in range(16)] if math.isnan(fy) else [])
for dt in [0,-1/60,.1]:
 for correction in [-.12,-.02,0,.02,.12]:
  basis=identity[:];basis[4]=-correction
  parent(0x504df0,p=[patch(BODIES+0x6c,'<16f',*basis),patch(PHYS+0x8c,'<f',dt)],label='upright signed time step')
# The zero product must preserve the unordered outcome; there are no writes.
basis=identity[:];basis[4]=-1;basis[5]=math.inf
parent(0x504df0,p=[patch(BODIES+0x6c,'<16f',*basis)],label='upright zero-times-infinity prevents rotation')

case([call(0x460b80,BODIES)],label='capture material event owner constructor')
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
module=ast.parse(task_source);chosen=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='attached_events']
exec(compile(ast.Module(body=chosen,type_ignores=[]),'<material event attachment>','exec'))
for material in [0,1,255,256,0xffffffff]:
 for previous in [0,1,255]:
  b=air_config();p=[patch(SKATER_STATE+0xe1,'<B',previous)]
  case(body_setup()+[call(0x4fc470,PHYS,[material])],b.patches()+p,label='state and sound material full argument versus low byte')
for target,value in [(0,0),(PHYS+0x1528,SKATER_STATE2),(PHYS+0x1514,SOUND2)]:
 b=air_config();p=attached_events()+[patch(SKATER_STATE+0xe1,'<B',255),patch(GOBS+4,'<4I',target,value,4 if target else 0,0xd3fde02a)]
 s=case(body_setup()[1:]+[call(0x41d1d0,SCRIPTS+0xbc,[BODIES]),call(0x4fc470,PHYS,[3])],b.patches()+p,label='actual material QB callback replaces live component')[-1]
 s['callbacks']+=oracle.word(GOBS);assert oracle.word(GOBS)==1

assert all(branches[name] for name in air_branches.values())
scope='Ten complete airborne prerequisites: pitch input 504910, incremental transfer orientation 504a60, upright correction 504df0, Z rotation, X premultiplication, vector magnitude alignment and threshold clearing, two age helpers and state/sound material propagation. All original game callees execute, including timers, stat evaluation, matrix interpolation/inversion and actual material QB delivery with state/sound replacement. Exact signed FILD cutoff, opposing inputs, full-width timestamps, overlapping vectors, nonfinite arithmetic and four-frame transfer sequences are covered. Typed arithmetic NaNs classify only in declared outputs; raw copy/no-write bytes remain exact. Existing math adapters retain the documented x87 transcendental limitation. Generic event-owner construction and terminating QB, successful allocation and required components are fixture contracts. No full airborne parent, skater startup or playable training claim.'
fixture={'base':BASE,'memory':'airborne-motion-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'airborne-motion-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original airborne prerequisites:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_airborne_motion_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'grounded-update-callbacks.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
