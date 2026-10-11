"""Compare airborne collision parents and their owner/reference prerequisites."""
from pathlib import Path
task_source=Path(__file__).with_name('verify_grounded_update.py').read_text()
exec(compile(task_source.split('\nfor speed in [0,100]:')[0].replace("'grounded-update.json'","'airborne-collision.json'"),'<airborne collision prerequisites>','exec'))
NEW=[(0x4ffdb0,'thug_skater_try_raised_path',1,'byte',False,False,True),
 (0x504ee0,'thug_skater_resolve_overhead',0,'byte',False,False,True),
 (0x4f8200,'thug_collision_probe_copy_initialize',1,'word',False,False,True),
 (0x43eb80,'thug_skater_moving_contact_set_owner',1,'word',True,False,True)]
for row in [(0x413000,'thug_moving_collision_initialize',1,'word',False,False,True),(0x412f90,'thug_moving_collision_set_position',1,'void',False,False,True),(0x40ae40,'thug_moving_collision_set_owner',1,'void',False,False,True)]:bind(*row)
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
for row in [(0x41c350,'thug_collision_probe_release',0,'void',False,False,True),(0x427c70,'thug_skater_moving_contact_release',0,'void',True,False,True)]:bind(*row)
ROOTS.update([0x4ffdb0,0x504ee0])
for at in [0x4ffdb0,0x4ffdf2,0x500010,0x504ee0,0x504f02,0x50519c,0x5051a5]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
for at in [0x417760,0x4637c0,0x4637e0,0x406200,0x4024d0,0x402440,0x4f8160,0x416e70]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
air_branches={0x4ffddb:'raised_gate',0x4ffe7c:'raised_lower_previous',0x4ffe95:'raised_higher_previous',0x4ffeca:'raised_first_accepted',0x4fff5d:'raised_accepted',0x4fffb5:'raised_rejected',0x4fffd5:'raised_first_miss',0x504efc:'overhead_inverted',0x504f3f:'overhead_recent',0x504f47:'overhead_configured',0x50504b:'overhead_first_accepted',0x50511b:'overhead_second_hit',0x505158:'overhead_second_miss',0x505181:'overhead_project_velocity'}
branch_at.update(air_branches)
for at in air_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
PROBE_A,PROBE_B,AIR_PREVIOUS,AIR_OWNER=0x1661000,0x1661100,0x1661200,0x1662000
copy(PROBE_A,initial[PHYS+0xa8-BASE:PHYS+0x158-BASE]);copy(PROBE_B,b'\x91'*0xb0);copy(AIR_OWNER,bytes(0x200));put(AIR_OWNER+0x6c,'<16f',*identity);put(AIR_OWNER+0x4c,'<4f',10,20,30,1)
initial=bytes(memory);oracle.initial=initial
collision_outcomes=Counter();query_observations=[];last_probe=0

def probe_trace(cpu,at,size,user):
 global last_probe
 if active_floor_root not in [0x4ffdb0,0x504ee0]:return
 if at==0x4172f0:last_probe=cpu.reg_read(UC_X86_REG_ECX);return
 hit=cpu.reg_read(UC_X86_REG_EAX)&255
 label={0x4ffeaa:'raised_first',0x4fff59:'raised_second',0x505004:'overhead_first',0x505117:'overhead_second'}[at]
 row={'case':len(labels),'stage':label,'hit':hit,'segment':bytes(cpu.mem_read(last_probe,32)).hex()}
 if hit:
  row.update(normal=bytes(cpu.mem_read(last_probe+0x88,16)).hex(),point=bytes(cpu.mem_read(last_probe+0x78,16)).hex(),owner=oracle.word(last_probe+0x98))
  collision_outcomes[label+('_moving' if row['owner'] else '_static')]+=1
  normal_y=struct.unpack('<4f',bytes.fromhex(row['normal']))[1]
  if label=='raised_first' and not normal_y>.5:collision_outcomes['raised_first_bad_normal']+=1
  if label=='overhead_first' and normal_y>-.10000000149011612:collision_outcomes['overhead_first_bad_normal']+=1
 collision_outcomes[label+('_hit' if hit else '_miss')]+=1;query_observations.append(row)
for at in [0x4172f0,0x4ffeaa,0x4fff59,0x505004,0x505117]:oracle.cpu.hook_add(UC_HOOK_CODE,probe_trace,begin=at,end=at)
air_base_case=case

def case(calls,p=(),changes=None,label='airborne collision'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 return air_base_case(calls,p,changes,label)

def air_config(height=64,step=16,window=100):
 b=grounded_config(numbers={0x786b3272:step,0x542cf0c7:height});b.symbol(0x2757ed2c,1,window);return b

def parent(at,args=(),p=(),b=None,changes=None,label='airborne collision',before=(),repeat=1):
 retained_caches.clear();b=b or air_config();start=len(query_observations)
 stages=case(body_setup()+list(before)+[call(at,PHYS,[*args,QUERY]) for _ in range(repeat)],b.patches()+list(p),changes,label)
 for s in stages:
  if s['fn'] in ['0x4ffdb0','0x504ee0']:s['stack_objects']=list(retained_caches.values());s['float_fields']=[]
 for s in stages:
  if s['fn']==hex(at):collision_outcomes[hex(at)+('_accepted' if s['result'] else '_rejected')]+=1
 rows=query_observations[start:]
 for a,b in zip(rows,rows[1:]):
  if not a['stage'].endswith('_first') or not b['stage'].endswith('_second') or not a['hit'] or not b['hit']:continue
  if a['normal']!=b['normal']:collision_outcomes['different_normals_'+hex(at)]+=1
  n0=struct.unpack('<4f',bytes.fromhex(a['normal']));n1=struct.unpack('<4f',bytes.fromhex(b['normal']))
  if sum((n0[(j+1)%3]*n1[(j+2)%3]-n0[(j+2)%3]*n1[(j+1)%3])**2 for j in range(3))>1e-6:collision_outcomes['nonparallel_normals_'+hex(at)]+=1
 return stages[-1],rows

# Generic fresh-storage copy constructors retain raw result padding and words,
# while inserting an independent reference in the same actual owner chain.
for owner in [0,GOWNER,AIR_OWNER]:
 for repeats in [1,2,3]:
  p=[patch(PROBE_A,'<8I',0x7f812345,0x80000000,0xff800000,0x3f800000,1,2,3,4),patch(PROBE_A+0xa8,'<I',0x98765432)]
  calls=[call(0x41d1d0,PROBE_A+0x98,[owner])]
  calls += [call(0x4f8200,PROBE_B+j*0x200,[PROBE_A]) for j in range(repeats)]
  calls += [call(0x41c350,PROBE_B+j*0x200) for j in range(repeats-1,-1,-1)]
  calls += [call(0x41c350,PROBE_A)]
  case(calls,p,label='probe copy construction links and releases actual references')
for old in [0,GOWNER,AIR_OWNER]:
 for owner in [GOWNER,AIR_OWNER]:
  for counter in [0,100,0xffffffff]:
   calls=([call(0x43eb80,GROUND_GATE,[old])] if old else [])+[call(0x43eb80,GROUND_GATE,[owner]),call(0x43eb80,GROUND_GATE,[owner]),call(0x427c70,GROUND_GATE)]
   case(calls,changes={0x7d1ec8:counter,0x696d60:0x80000000},label='explicit contact owner replaces same changed and empty contact')

parent(0x4ffdb0,[AIR_PREVIOUS],p=[patch(SKATER_STATE+0x70,'<B',255)],label='raised path resistance early gate')
for y in [-1,-0.,0,1]:
 parent(0x504ee0,p=[patch(BODIES+0x80,'<f',y)],label='overhead orientation up gate')
for age in [0,99,100,101,0x7fffffff,0x80000000,0xffffffff]:
 for threshold in [0,100,0xffffffff]:
  parent(0x504ee0,p=[patch(PHYS+0x4e0,'<I',(1666-age)&0xffffffff)],b=air_config(window=threshold),label='overhead unsigned cooldown boundary')

up_cases=[];overhead_cases=[]
for i in [30,31,33,34,40,43,45,46,47,48,49,52,53,56,70,74,85,129,278,400]:
 q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 for current_y,previous_y in [(-1,-12),(-12,-1),(-1,-1),(2,-1)]:
  for dx,dz in [(0,0),(20,0),(200,0),(0,200),(-200,-200)]:
   current=[point[0],point[1]+current_y,point[2],1];previous=[point[0]+dx,point[1]+previous_y,point[2]+dz,1]
   p=[patch(BODIES+0x4c,'<4f',*current),patch(AIR_PREVIOUS,'<4f',*previous)]
   result,observations=parent(0x4ffdb0,[AIR_PREVIOUS],p=p,label=f'raised training surface {i} heights {current_y}/{previous_y} offset {dx}/{dz}')
   up_cases.append((i,p,result['result'],observations))
# Genuine non-upward surfaces and larger offsets cover first-hit rejection.
for i in [4,5,13,14,29,51,93,105,150,159,160,178,189,200,203]:
 data=bytes.fromhex(loader['queries'][i]['result']);point=struct.unpack_from('<4f',data,16)
 p=[patch(BODIES+0x4c,'<4f',point[0],point[1]-2,point[2],1),patch(AIR_PREVIOUS,'<4f',point[0],point[1]-8,point[2],1)]
 parent(0x4ffdb0,[AIR_PREVIOUS],p=p,label=f'raised scan rejects non-upward training face {i}')

for i,q in enumerate(loader['queries']):
 data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 if normal[1]>-.1:continue
 for distance in [1,5,24,80]:
  for height in [64,256]:
   position=[point[j]+normal[j]*distance for j in range(3)]+[1]
   p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0xac,'<4f',30,200,-10,1)]
   result,observations=parent(0x504ee0,p=p,b=air_config(height=height),label=f'overhead training face {i} distance {distance} height {height}')
   overhead_cases.append((i,height,p,result['result'],observations))

# Move actual training geometry away from the static world. Constructors and
# position/owner setters execute in the original code; query outcomes are not
# intercepted. A second real object supplies an obstruction or a lower floor.
def moving_world(indices,targets,position_w=0):
 p=[];before=[]
 for j,(i,target) in enumerate(zip(indices,targets)):
  data=bytes.fromhex(loader['queries'][i]['result']);point=struct.unpack_from('<4f',data,16)
  instance=struct.unpack_from('<I',data,0x30)[0];geometry=struct.unpack_from('<I',initial,instance+12-BASE)[0]
  position=M0+j*16
  p += [patch(position,'<4f',*[target[k]-point[k] for k in range(3)],position_w),patch(COLL_NODES+j*16,'<4I',0,RUNTIME+j*256,0,COLL_NODES+(j+1)*16)]
  before += [call(0x413000,RUNTIME+j*256,[geometry]),call(0x412f90,RUNTIME+j*256,[position]),call(0x40ae40,RUNTIME+j*256,[AIR_OWNER if j==0 else GOWNER])]
 p.append(patch(COLL_NODES+len(indices)*16,'<4I',0,0xffffffff,0,COLL_NODES+len(indices)*16))
 return p,before

for obstructed in [False,True]:
 for distance in [-2,0,2]:
  for position_w in [0,1]:
   target=[50000,20000,50000]
   indices=[46,0] if obstructed else [46]
   targets=[target,[target[0],target[1]+16,target[2]-100]] if obstructed else [target]
   p,before=moving_world(indices,targets,position_w)
   p += [patch(BODIES+0x4c,'<4f',target[0],target[1]+distance,target[2],1),patch(AIR_PREVIOUS,'<4f',target[0],target[1]-8,target[2]-200,1)]
   parent(0x4ffdb0,[AIR_PREVIOUS],p=p,before=before,label=f'raised moving floor wall {obstructed} distance {distance} W {position_w}')
for ceiling in [4,93,178]:
 for lower_floor in [False,True]:
  for position_w in [0,1]:
   target=[50000,20000,50000]
   indices=[ceiling,46] if lower_floor else [ceiling]
   targets=[target,[target[0],target[1]-32,target[2]]] if lower_floor else [target]
   p,before=moving_world(indices,targets,position_w)
   p += [patch(BODIES+0x4c,'<4f',target[0],target[1]-5,target[2],1),patch(BODIES+0xac,'<4f',30,200,-10,1)]
   parent(0x504ee0,p=p,before=before,repeat=2 if lower_floor and position_w else 1,label=f'overhead moving ceiling {ceiling} lower floor {lower_floor} W {position_w}')

# A sideways up-axis can hit a wall without passing the ceiling-normal test.
for i in [0,1,2,3]:
 data=bytes.fromhex(loader['queries'][i]['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 up=[-normal[0],0,-normal[2],0];forward=[0,1,0,0];right=[-up[2],0,up[0],0]
 p=[patch(BODIES+0x4c,'<4f',point[0]+normal[0]*5,point[1],point[2]+normal[2]*5,1),patch(BODIES+0x6c,'<16f',*(right+up+forward+[0,0,0,1]))]
 parent(0x504ee0,p=p,label=f'overhead scan rejects wall normal {i}')

assert all(branches[name] for name in air_branches.values())
for name in ['raised_first_moving','raised_second_moving','overhead_first_moving','overhead_second_moving','nonparallel_normals_0x504ee0','raised_first_bad_normal','overhead_first_bad_normal']:assert collision_outcomes[name]>0,name

for at,name in air_branches.items():print('BRANCH',name,branches[name],flush=True)
print('OUTCOMES',dict(collision_outcomes),flush=True)
scope='Four complete original routines: raised-path collision 4ffdb0, overhead response 504ee0, fresh probe copy constructor 4f8200 and explicit moving-contact owner replacement 43eb80. Full training static and moving collision, both probe sequences, normal rejection, timer wrap, owner-chain changes and heap effects execute through original game callees. First normal is retained for velocity while the second probe supplies final position. All arena/global bytes compare exactly for finite valid geometry. Query-context relocation and the existing heap adapter are instrumentation boundaries; required components, fresh constructor storage and successful allocation are fixture contracts. Generic event-owner construction is not skater startup. Full airborne movement, state integration and playable training remain unfinished.'
fixture={'base':BASE,'memory':'airborne-collision-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'airborne-collision-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original airborne collision:',len(labels),sum(oracle.counts.values()),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_airborne_collision_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'outcomes':dict(collision_outcomes),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
