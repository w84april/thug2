"""Original-instruction comparisons for complete floor/transition handling."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_transfer_apply.py').read_text().split('identity=')[0]
exec(compile(prefix.replace("'transfer-apply.json'","'floor.json'"),str(Path(__file__).with_name('verify_transfer_apply.py')),'exec'))
NEW=[(0x46b900,'thug_input_button_elapsed_8',0,'word',False,False,True),(0x580440,'thug_skater_get_integer_parameter',3,'word',False,False,False),(0x404dd0,'thug_matrix_rotation_x',2,'word',False,False,False),(0x420140,'thug_quaternion_multiply',1,'word',False,False,True),(0x420ac0,'thug_quaternion_axis_angle',2,'word',False,False,True),(0x420b50,'thug_quaternion_rotate',2,'word',False,False,True),(0x4058e0,'thug_matrix_interpolation_reverse',0,'void',False,False,True),(0x405a20,'thug_matrix_interpolate',2,'void',False,False,True)]
for row in NEW:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
functions['0x404dd0']['float_args']=[1]
for fn in [0x420ac0,0x405a20]:functions[hex(fn)]['float_args']=[1]
identity=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
rng=random.Random(0x509bd0)
for timestamp in [0,1,1666,1667,0x7fffffff,0xffffffff]:
 for counter in [0,100,0xffffffff]:
  case([call(0x46b900,INPUT+0x20)],[patch(INPUT+0x28,'<I',timestamp)],{0x7d1ec8:counter,0x696d60:0x80000000},label='second button timestamp and signed wrap')
for enabled in [0,1]:
 for local in [None,0,0xffffffff,0x80000000]:
  b=config();key=0x9d2f8cc8
  b.symbol(0x8cbc89dd,10,b.structure([] if local is None else [(key,1,local)]));b.symbol(key,1,123)
  p=[patch(BODIES+0xbc,'<B',enabled),patch(MOTION+16,'<I',PHYS)]
  case([call(0x580440,args=[key,1,BODIES])],b.patches()+p,label='integer skater parameter local/fallback')
quaternions=[[0,0,0,1],[1,0,0,0],[0,0,0,0]]
for scale in [1e-30,1e-10,1,1e10,1e30]:
 for _ in range(8):quaternions.append([rng.uniform(-scale,scale) for j in range(4)])
quaternions += [[math.nan,1,2,3],[math.inf,0,0,1],[0,0,0,math.inf]]
for i,q in enumerate(quaternions):
 v=quaternions[(i+11)%len(quaternions)]
 for offset in [0,4,16]:
  p=[patch(M0,'<8f',*(q+v))]
  s=case([call(0x420140,M0,[M0+offset])],p,label='quaternion product with overlap')[0];s['float_fields']=[M0+j*4 for j in range(4)]
 for output in [MOUT,M0,M1]:
  s=case([call(0x420b50,M0,[output,M1])],[patch(M0,'<4f',*q),patch(M1,'<4f',*v)],label='quaternion vector rotation and aliases')[0];s['float_fields']=[output+j*4 for j in range(4)]
 for angle in [0,.01,math.pi,-math.pi/2,math.nan]:
  s=case([call(0x420ac0,M0,[M0,bits(angle)])],[patch(M0,'<4f',*q)],label='quaternion axis-angle in place')[0];s['float_fields']=[M0+j*4 for j in range(4)]
for angle in [0,-0.,.01,-.01,math.pi,-math.pi/2,1e20,math.nan]:
 s=case([call(0x404dd0,args=[MOUT,bits(angle)])],label='X-axis rotation')[0];s['float_fields']=[MOUT+j*4 for j in range(16)]
for angle in [0,1,math.pi,6.2831854820251465,math.nan]:
 s=case([call(0x4058e0,INTERP)],[patch(INTERP+0x80,'<5f',1,2,3,4,angle)],label='reverse interpolation axis and angle')[0];s['float_fields']=[INTERP+0x80+j*4 for j in range(5)]
for small in [0,1,255]:
 for factor in [-1,0,.00001,.5,1,2,math.nan]:
  for shift in [None,0,4,16,64,80]:
   a=[rng.uniform(-3,3) for _ in range(16)];b=[rng.uniform(-3,3) for _ in range(16)]
   output=MOUT if shift is None else INTERP+shift
   p=[patch(INTERP,'<37fB',*(a+b+[.4,.2,.1,1,1.3]),small)]
   s=case([call(0x405a20,INTERP,[output,bits(factor)])],p,label='matrix interpolation range, branch and overlap')[0];s['float_fields']=[output+j*4 for j in range(16)]

# Complete movement parents are exercised below, after their prerequisites.

# All four parents execute their original game callees, including nested scans.
ROOTS={0x4fee10,0x505f70,0x507120,0x509bd0}
for row in [(0x4fee10,'thug_skater_find_alternate_transfer',6,'byte',False,False,True),(0x505f70,'thug_skater_try_alternate_transfer',0,'byte',True,True,True),(0x507120,'thug_skater_leave_transition',1,'void',True,True,True),(0x509bd0,'thug_skater_handle_floor',0,'void',True,True,True)]:
 bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
active_floor_root=0;retained_caches={}
def floor_observe(cpu,address,size,user):
 global active_floor_root
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address in ROOTS and oracle.word(sp)==oracle.stop:
  active_floor_root=address;cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 elif address==0x40ab40 and active_floor_root:
  ptr=cpu.reg_read(UC_X86_REG_ECX)
  slot=next(i for i in range(8) if oracle.word(0x6918ec+4*i)==ptr and oracle.word(0x69190c)&(1<<i))
  # The nested function's stack storage may be reused before the parent returns.
  # Only its retained identity/inactive registry bit remains defined then.
  blocks=[]
  if active_floor_root==0x4fee10:
   count=oracle.word(ptr+0xfc0);assert count<=500
   blocks=[[0,bytes(cpu.mem_read(ptr,32)).hex()],[0xfc0,bytes(cpu.mem_read(ptr+0xfc0,12)).hex()],[32,bytes(cpu.mem_read(ptr+32,count*8)).hex(),list(range(0,count*8,4))]]
  retained_caches[slot]={'original':ptr,'global':['thug_collision_cache_registry',4*slot],'mask':['thug_collision_cache_mask',slot,0],'size':0xfcc,'blocks':blocks}
 elif oracle.word(sp)==oracle.stop:
  cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)));active_floor_root=0
for at in [*ROOTS,0x40ab40,0x4ff122,0x50643a,0x5066a9,0x506b9f,0x50738d,0x5074f7,0x50a24e,0x50a2b0]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
for at,name in {0x4ff125:'alternate_contact',0x50643b:'alternate_target',0x50671e:'alternate_blocked',0x506743:'alternate_apply',0x506ac0:'alternate_script',0x507228:'exit_response',0x5067a7:'alternate_opposed',0x506764:'alternate_plane',0x506a2c:'alternate_reverse',0x509de4:'floor_leave',0x509eb4:'floor_skatable',0x50a02e:'floor_tangent',0x50a0ba:'floor_contact',0x50a168:'floor_landing',0x50a1bf:'floor_contact_changed',0x50a24f:'floor_transfer_input'}.items():
 branch_at[at]=name;oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
for at in [0x4feba0,0x4fea50,0x5196a0,0x46b920,0x580440,0x580400,0x405a20,0x4058e0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
import ast
reuse=Path(__file__).with_name('verify_transfer_apply.py')
module=ast.parse(reuse.read_text());chosen=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['event_patches','transfer_program']]
exec(compile(ast.Module(body=chosen,type_ignores=[]),str(reuse),'exec'))

def floor_config(**kw):
 b=config();transfer_program(b)
 numbers={0xe4d79235:6,0xef161c2a:45,0x4138283e:60,0x899ba3d0:8,0x13f33b41:.2,0x848c5cd6:.8,0xd757f4bb:15,0x3eede4d3:30,0x78384871:1,0xd8120182:.1}
 numbers.update(kw.get('numbers',{}))
 for key,value in numbers.items():b.symbol(key,2,bits(value))
 for key,value in {0x9d2f8cc8:100,0x6bb5b751:200,0x19fb78fa:0,**kw.get('integers',{})}.items():b.symbol(key,1,value)
 # Install real terminating bytecode for both additional transfer scripts.
 slots={}
 for at,data in b.extra:
  if CACHETABLE+32<=at<CACHETABLE+80:slots[at]=bytes.fromhex(data)
 for name in [0xa5179e9e,0x283bb5d6]:
  code=b.alloc(b'\x01\x24');entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
  previous=slots.get(slot,initial[slot-BASE:slot-BASE+12]);link=b.alloc(previous)
  slots[slot]=struct.pack('<3I',name,entry,link);b.extra.append(raw(slot,slots[slot]));b.symbol(name,7,code)
 b.extra += [patch(CACHETABLE+8,'<I',14),patch(MOTION+16,'<I',PHYS),patch(PHYS+0x18,'<16f',*identity),patch(PHYS+0x58,'<4f',0,1,0,0),patch(PHYS+0x8c,'<f',1/60),raw(PHYS+0x17c,bytes(0x50))]
 return b

def floor_parent(at,args=(),b=None,p=(),changes=None,label='floor parent',before=(),attached=False):
 retained_caches.clear();b=b or floor_config()
 stages=case((body_setup()[1:] if attached else body_setup())+list(before)+[call(at,PHYS,[*args,QUERY])],b.patches()+list(p),changes,label)
 stage=stages[-1];stage['stack_objects']=list(retained_caches.values())
 stage['float_fields']=[BODIES+off for off in range(0x4c,0xbc,4)]+[PHYS+off for off in list(range(0x18,0x90,4))+list(range(0x258,0x29c,4))+list(range(0x3b0,0x4e0,4)) if off!=0x484]+[SKATER_STATE+0xe4+i*4 for i in range(4)]+[RESULT+i*4 for i in range(8)]
 stage['global_float_indices']=[index[0x7ccdbc+i*4] for i in range(4)]
 return stage
for at,args in [(0x4fee10,[FROM,ORIGIN,RESULT+36,RESULT,RESULT+16,RESULT+37]),(0x505f70,[]),(0x507120,[0]),(0x507120,[1]),(0x509bd0,[])]:
 floor_parent(at,args,p=[patch(FROM,'<4f',1,0,0,0),patch(ORIGIN,'<4f',-1,0,0,0)],label='complete parent clear-space or input gate')
for flags in [(1,0,0,0,0,0),(1,1,0,0,0,0),(1,0,1,0,0,0),(1,0,0,1,0,0),(1,0,0,0,1,0),(0,0,0,0,0,1)]:
 p=[patch(INPUT+off,'<B',value) for off,value in zip([0x20,0x60,0x80,0x160,0x180,0xc0],flags)]
 if flags[-1]:p.append(patch(INPUT+0x120,'<B',1))
 for delay in [100,1666,1667,0x80000000]:
  floor_parent(0x507120,[0],floor_config(integers={0x9d2f8cc8:delay}),p,label='transition signed input delay and competing buttons')
for surface in [0,1,255]:
 for buttons in [0,1]:
  p=[patch(SKATER_STATE+0x40,'<B',surface),patch(PHYS+0x68,'<4f',.6,.8,0,0),patch(INPUT+0xc0,'<B',buttons),patch(INPUT+0x120,'<B',buttons)]
  floor_parent(0x509bd0,p=p,label='floor departure transition flags and transfer input')
# Full static training scene; vary signed contact distance and prior orientation.
training_cases=[]
for i in [0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]:
 q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 for distance in [-2,0,2,10,100]:
  position=[point[j]+normal[j]*distance for j in range(3)]+[1]
  forward=[-normal[2],0,normal[0],0];length=math.hypot(forward[0],forward[2])
  forward=[v/length for v in forward] if length else [0,0,1,0]
  right=[normal[1]*forward[2]-normal[2]*forward[1],normal[2]*forward[0]-normal[0]*forward[2],normal[0]*forward[1]-normal[1]*forward[0],0]
  basis=right+list(normal)+forward+[0,0,0,1]
  p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',position[0]-forward[0]*10,position[1],position[2]-forward[2]*10,1),patch(BODIES+0x6c,'<16f',*basis),patch(PHYS+0x18,'<16f',*basis),patch(PHYS+0x58,'<4f',*normal),patch(PHYS+0x68,'<4f',*normal),patch(BODIES+0xac,'<4f',forward[0]*100,200,forward[2]*100,0)]
  training_cases.append((i,distance,p,normal,point))
  floor_parent(0x509bd0,p=p,label=f'training floor {i} distance {distance}')
 # Independent complete contact scan, two relative normal signs.
 for sign in [-1,1]:
  horizontal=[normal[0],0,normal[2],0];length=math.hypot(horizontal[0],horizontal[2]);direction=[v/length for v in horizontal] if length else [1,0,0,0]
  p=[patch(BODIES+0x4c,'<4f',point[0]-direction[0]*16,point[1]+20,point[2]-direction[2]*16,1),patch(FROM,'<4f',*direction),patch(ORIGIN,'<4f',*[sign*v for v in direction])]
  floor_parent(0x4fee10,[FROM,ORIGIN,RESULT+36,RESULT,RESULT+16,RESULT+37],p=p,label=f'training alternate scan {i} sign {sign}')
for i,distance,p,normal,point in training_cases:
 if distance!=2:continue
 for button in [0,0x60,0x80]:
  floor_parent(0x505f70,p=p+([patch(INPUT+button,'<B',1)] if button else []),label=f'training alternate parent {i} input {button}')


# Raise the approach above surrounding geometry and vary upward flight speed.
for i,distance,p,normal,point in training_cases:
 if distance!=2 or i not in [34,70,129]:continue
 for height in [10,100,300]:
  for speed in [200,1000,2000]:
   overrides=[patch(BODIES+0x50,'<f',point[1]+height),patch(BODIES+0xb0,'<f',speed)]
   floor_parent(0x505f70,p=p+overrides,label=f'raised alternate {i} height {height} speed {speed}')
# Original script delivery and native activation can replace a live component.
case([call(0x460b80,BODIES)],label='capture floor event-owner constructor')
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
for event in [0xa7662059,0xd3fde02a]:
 for target,value in [(PHYS+0x1514,SOUND2),(PHYS+0x1528,SKATER_STATE2),(GATE+0x26,1)]:
  b=floor_config();natives(b);b.goal(1,params=[(0,13,0x4599b58c)],active=0)
  program(b,5,b'\x01'+command(0,0x101)+b'\x01\x24')
  script=bytearray(244)
  for offset,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,offset,v)
  p=[raw(BODIES,body_base),raw(SCRIPTS,script),patch(BODIES+0x10,'<I',SCRIPTS),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',event,5,0,0,0),patch(DIAG+8,'<2I',target,value),patch(MOTION+16,'<I',SCORE_COMPONENTS)]
  if event==0xd3fde02a:
   p+=next(c[2] for c in training_cases if c[0]==34 and c[1]==2)+[patch(SKATER_STATE+0xe1,'<B',255)]
  p+=player_patches(1,0,1,1)
  floor_parent(0x509bd0,b=b,p=p,before=ui_setup()+[call(0x41d1d0,SCRIPTS+0xbc,[BODIES])],attached=True,label='floor mode/material event invokes actual native goal activation and mutation')
  assert oracle.word(DIAG)==1,(hex(event),hex(target),oracle.word(DIAG))

scope='Twelve complete original routines: floor handler 509bd0, alternate contact scan 4fee10, alternate transfer 505f70, transition exit 507120, second button timer, integer parameter getter, three quaternion routines, X rotation and two interpolation routines. 940 cases/1846 calls include 113 floor calls, real static training geometry, six complete alternate applications (four plane and two opposed), eighteen deferred blocked returns and six actual QB/native goal callbacks replacing sound/state or the response gate. All game callees execute. Automatic cache identity and inactive registry bits are checked; defined cache fields are checked for direct scan roots, while expired nested stack storage is not dereferenced. Generic event-owner construction supplies valid fixtures; full skater construction is not recovered. SDK tan models the floor FPTAN after clamped acos, without physical x87 transcendental accuracy claims. Required components/typed configuration, valid fixed-capacity caches, terminating QB graphs and successful allocations are contracts. Arithmetic NaNs classify only at declared float outputs; raw copies and other bytes remain exact. Original training remains unplayable; balance, grounded integration, startup, rendering, input and audio remain.'
fixture={'base':BASE,'memory':'floor-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'floor-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_floor_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'callee_coverage_note':'Raw observation-hook hits, not unique invocation totals. The floor fixture adds second observers for 580440, 405a20 and 4058e0 after the prerequisite cases. Root counts, branch counts and diagnostic callback counts are separate and not duplicated.','branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
