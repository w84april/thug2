"""Compare complete airborne turning and its live scoring/UI/QB call graph."""
from pathlib import Path
import ast
spin_fixture_source=Path(__file__).with_name('verify_spin_score.py').read_text()
exec(compile(spin_fixture_source.split('\nrng=random.Random(0x563f30)')[0].replace("'spin-score.json'","'airborne-spin.json'"),'<spin scoring graph>','exec'))
spin_functions=[n for n in ast.parse(spin_fixture_source).body if isinstance(n,ast.FunctionDef) and n.name in ['spin_config','spin_entries']]
exec(compile(ast.Module(body=spin_functions,type_ignores=[]),'<spin scoring helpers>','exec'))
bind(0x504060,'thug_skater_spin_input',0,'void',True,True,True)
for at in [0x504060,0x46b7e0,0x580790,0x4022c0,0x405fd0,0x406630,0x623630,0x564be0]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
put(PHYS+0x1520,'<I',SCORE_COMPONENTS);put(NAME_CONTEXT+0x13a4,'<f',0)
put(PHYS+0x288,'<4f',1,0,0,0)
initial=bytes(memory);oracle.initial=initial
turn_branches={0x50409d:'clear_transfer_auto',0x5040d7:'tap_left_edge',0x504110:'tap_right_edge',0x504180:'tap_rate',0x5041b2:'tap_overshoot',0x5041c7:'tap_remaining',0x50423b:'shoulder_left',0x50430d:'shoulder_right',0x5042a1:'shoulder_left_cancel',0x504375:'shoulder_right_cancel',0x5043b0:'digital_left',0x504421:'digital_right',0x504403:'digital_left_cancel',0x504476:'digital_right_cancel',0x5044bf:'digital_cutoff',0x5044d0:'digital_ramp',0x50451d:'auto_turn',0x504568:'auto_angle',0x5045c6:'auto_overshoot',0x5045d4:'auto_clear',0x50460c:'rotation',0x5046a3:'vert_score_gate',0x5046e0:'vert_score',0x504708:'ordinary_score'}
branch_at.update(turn_branches)
for at in turn_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
rng=random.Random(0x504060)
turn_base_case=case
turn_float_fields=[BODIES+0x6c+4*i for i in range(16)]+[PHYS+0x18+4*i for i in range(16)]+[PHYS+0x30c,NAME_CONTEXT+0x13a4]
def case(calls,p=(),changes=None,label='airborne spin'):
 stages=turn_base_case(calls,p,changes,label)
 for stage in stages:stage['float_fields']=turn_float_fields
 return stages

def turn_config(rate=2,tap_rate=4,cutoff=100,ramp=300,shoulder_cutoff=100,cancel=500,auto_angle=10,auto_speed=3,slop=10):
 b=spin_config(slop)
 for name,value in [(0x4957db43,rate),(0xf7a2acc1,tap_rate)]:
  pair=b.alloc(struct.pack('<I2f',0,value,value));b.symbol(name,10,b.structure([(0,5,pair)]))
 for name,value in [(0xa092b2be,cutoff),(0x5d756349,ramp),(0xa5a02449,shoulder_cutoff),(0xabdd3395,cancel),(0x61224f2e,auto_angle),(0x9db33213,auto_speed)]:b.symbol(name,2,bits(value))
 return b

def turn(p=(),b=None,changes=None,repeat=1,label='complete airborne spin',score=(),attached=False):
 b=b or turn_config();calls=body_setup()+setup()+numeric_setup()
 patches=spin_entries(count=2)+list(score)+list(p)
 if attached:
  script=bytearray(244)
  for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
  patches += [patch(BODIES+0x10,'<I',SCRIPTS),raw(SCRIPTS,script),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',spin_event,spin_event,0,0,1)]
  bucket,head,node=0x1662400,0x1662480,0x16624a0
  patches += [patch(LISTENERS,'<6I',2,bucket,1,0xffffffff,0,0),raw(bucket,bytes(48)),patch(bucket+(spin_event&3)*12,'<3I',spin_event,head,0),patch(head,'<5I',0x6478dc,0xffffffff,0,node,node),patch(node,'<5I',0x6478d8,SCRIPTS,0,head,head)]
  fields.update([SCRIPTS+0xec,head,node]);calls.append(call(0x41d1d0,SCRIPTS+0xbc,[BODIES]))
 calls += [call(0x504060,PHYS) for _ in range(repeat)]
 return case(calls,b.patches()+patches,changes,label)

def button(at,pressed=1,age=600,edge=0,now=1666):
 return [patch(INPUT+at,'<B3xI',pressed,(now-age)&0xffffffff),patch(INPUT+at+0x10,'<B',edge)]

# Each gate retains existing state; full-byte truth and timestamp wrap matter.
for gate in [0,1,255]:
 for flag78 in [0,1,255]:
  for flag68 in [0,1,255]:
   turn(p=[patch(PHYS+0x370,'<B',gate),patch(SKATER_STATE+0x78,'<B',flag78),patch(SKATER_STATE+0x68,'<B3sI',flag68,b'xyz',0x12345678)],changes={0x7d1ec8:0xffffffff,0x696d60:0x80000000},label='early gate and transfer auto-flag timestamp wrap')

for tap in [False,True]:
 for mask in range(4):
  for edges in range(4) if tap else [0]:
   for age in [0,100,101,500,501,0x7fffffff,0x80000000,0xffffffff] if not tap else [600]:
    p=button(0xa0,mask&1,age,edges&1)+button(0x100,mask>>1,age,edges>>1)
    p += [patch(PHYS+0x2da,'<B',255 if tap else 0),patch(SKATER_STATE+0x68,'<B',255)]
    turn(p=p,label=f'shoulder/tap mode {tap} held {mask} edge {edges} age {age}')
for remaining in [-math.pi,-.01,-0.,0.,.01,math.pi,1e30,math.nan]:
 for dt in [0,1/60,1,-.5]:
  p=[patch(PHYS+0x2da,'<B',1),patch(PHYS+0x30c,'<f',remaining),patch(PHYS+0x8c,'<f',dt)]
  turn(p=p,repeat=3 if remaining==.01 and dt>0 else 1,label='tap residual, exact zero, overshoot, negative timestep and consecutive frames')

for mask in range(4):
 for age in [0,99,100,101,299,300,301,500,501,0x7fffffff,0x80000000,0xffffffff]:
  p=button(0x60,mask&1,age)+button(0x80,mask>>1,age)+[patch(SKATER_STATE+0x68,'<B',255)]
  turn(p=p,label=f'directional mask {mask}, signed timer {age}')
for left,right in [(0,600),(600,0),(100,301),(301,100)]:
 turn(p=button(0x60,1,left)+button(0x80,1,right),label='second directional button overrides rate AND timer')
for cutoff,ramp in [(0,0),(300,100),(300,300),(-100,100),(16777216,16777220),(math.nan,300),(100,math.nan)]:
 for age in [0,100,300,16777215,16777216,16777217]:
  turn(p=button(0x60,1,age),b=turn_config(cutoff=cutoff,ramp=ramp),label='ramp endpoints, exact signed FILD comparisons and unordered thresholds')
for digital_gate in [0,1,255]:
 for shoulder in [0,1]:
  turn(p=button(0x60)+button(0xa0,shoulder)+[patch(SKATER_STATE+0xc0,'<B',digital_gate)],label='shoulder precedence over digital gate')

# Automatic turning uses clamped forward-Y, a signed angle and an overshoot cap.
for flag30 in [0,1,255]:
 for flag68 in [0,1,255]:
  for target in [(1,0,0,0),(-1,0,0,0),(0,0,1,0),(0,0,-1,0)]:
   p=[patch(SKATER_STATE+0x30,'<B',flag30),patch(SKATER_STATE+0x68,'<B',flag68),patch(PHYS+0x288,'<4f',*target)]
   turn(p=p,label='automatic turn flags and signed target angle')
for y in [-2,-1,-.5,0,.5,1,2,math.nan]:
 for threshold in [0,90,180,181,math.nan]:
  p=[patch(SKATER_STATE+0x30,'<B',1),patch(SKATER_STATE+0x68,'<B',1),patch(BODIES+0x90,'<f',y)]
  turn(p=p,b=turn_config(auto_angle=threshold),label='clamped forward vertical and automatic turn threshold equality')
for dt in [0,1/60,1,-1,1e-30,1e30]:
 for speed in [0,1,3,-3]:
  p=[patch(SKATER_STATE+0x30,'<B',1),patch(SKATER_STATE+0x68,'<B',1),patch(PHYS+0x8c,'<f',dt)]
  turn(p=p,b=turn_config(auto_speed=speed),label='automatic overshoot, zero/negative rate and timestep range')

# Complete scoring executes both displays and actual broadcast/native QB paths.
for flag30,flag78 in [(0,0),(1,0),(1,1)]:
 for total in [0,169.9,170,349.9,350,350.1,360,-360,719]:
  p=button(0xa0)+[patch(SKATER_STATE+0x30,'<B',flag30),patch(SKATER_STATE+0x78,'<B',flag78),patch(NAME_CONTEXT+0x13a4,'<f',total)]
  turn(p=p,score=spin_entries(b'Fakie\\_Ollie',count=2,ollie=True),label='vert spin-score gate versus ordinary scoring')
for i,notify in enumerate([NOTIFY,NUMERIC_NOTIFY]):
 for target,value,width in [(NAME_CONTEXT+0x13a4,bits(360),4),(PHYS+0x30c,bits(1),4),(PHYS+0x370,1,1),(SKATER_STATE+0xc0,255,1),(SCORE+0x6c,1,4)]:
  p=button(0xa0)+[patch(NAME_CONTEXT+0x13a4,'<f',179),patch(META+i*256+12,'<I',SPIN_NOTIFY_PROGRAM),patch(META+i*256+36,'<I',SPIN_NOTIFY_PROGRAM),patch(GOBS+4,'<4I',target,value,width,notify)]
  turn(p=p,repeat=2,label='real UI QB callback changes cumulative angle, turn state or score entry before next frame')
  assert oracle.word(GOBS)>0
for target,value,width in [(NAME_CONTEXT+0x13a4,bits(0),4),(PHYS+0x2da,1,1),(SKATER_STATE+0x68,255,1)]:
 p=button(0xa0)+[patch(NAME_CONTEXT+0x13a4,'<f',179),patch(GOBS+4,'<4I',target,value,width,spin_event)]
 turn(p=p,repeat=2,attached=True,label='spin broadcast executes cached QB and mutates next-frame turn state')
 assert oracle.word(GOBS)>0

# Real training surface bases and independent cached matrices through repeated frames.
for i in [0,13,34,70,129,278,488,545]:
 normal=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][i]['result']))
 forward=[-normal[2],0,normal[0],0];length=math.hypot(forward[0],forward[2]);forward=[x/length for x in forward] if length else [0,0,1,0]
 right=[normal[1]*forward[2],normal[2]*forward[0]-normal[0]*forward[2],-normal[1]*forward[0],0]
 for side in [0x60,0x80,0xa0,0x100]:
  p=button(side)+[patch(BODIES+0x6c,'<16f',*(right+list(normal)+forward+[0,0,0,1])),patch(PHYS+0x18,'<16f',*[rng.uniform(-2,2) for _ in range(16)])]
  turn(p=p,repeat=3,label=f'training basis {i}, button {side:x}, independent cached basis')

for dt,rate in [(0,math.nan),(1/60,math.nan),(1/60,math.inf),(-1/60,-math.inf),(math.nan,1),(math.inf,0),(1e-40,1e-40),(1e30,1e30)]:
 turn(p=button(0xa0)+[patch(PHYS+0x8c,'<f',dt)],b=turn_config(rate=rate),label='nonfinite and extreme rotation products with defined score conversion')
for value in [1e30,3e38,-3e38]:
 turn(p=[patch(PHYS+0x2da,'<B',1),patch(PHYS+0x30c,'<f',.1),patch(PHYS+0x8c,'<f',1e-38)],b=turn_config(tap_rate=value),label='tap rate retains wide exponent before residual test')
# A global integer endpoint can retain one more bit than its float spill.
for endpoint in [16777217,16777219,0x7fffffff]:
 for age in [16777216,16777217,16777218]:
  b=turn_config(cutoff=16777216);b.symbol(0x5d756349,1,endpoint)
  turn(p=button(0x60,1,age),b=b,label='integer global ramp endpoint retains exact value from QB getter')
# Mode-specific parameters apply to body-aware calls, while the shoulder
# cutoff deliberately receives a null body and must use the default set.
for shoulder_cutoff in [0,1000]:
 for mask in [1,2,3]:
  b=turn_config()
  b.symbol(0x8cbc89dd,10,b.structure([(0xa5a02449,2,bits(shoulder_cutoff))]))
  b.symbol(0xd3d12913,10,b.structure([(0xa5a02449,2,bits(10)),(0xa092b2be,2,bits(0)),(0x5d756349,2,bits(1)),(0xabdd3395,2,bits(1000))]))
  p=button(0xa0,mask&1)+button(0x100,mask>>1)+button(0x60)
  p += [patch(BODIES+0xbc,'<B',1),patch(PHYS+0x302,'<B',1),patch(SKATER_STATE+0x68,'<B',1)]
  turn(p=p,b=b,label='selected body parameter set versus null-body shoulder cutoff')
assert all(branches[name] for name in turn_branches.values()),{name:branches[name] for name in turn_branches.values()}
scope='Complete airborne spin update504060, with original tap/shoulder/directional input, unsigned-versus-signed elapsed time, ramp and automatic-turn handling, both Y rotations, cumulative angle, vert scoring gate and original spin scoring/UI/QB callees. Full fixture memory, globals, heap and callback traces compare. Repeated frames include actual native UI and spin-broadcast callbacks changing live turn state. Training collision normals supply real basis inputs; this is not complete airborne movement or playable training. Required typed parameters, registered score/components/widgets, valid lists and bounded fitting score strings retain original contracts. Existing SDK transcendental adapters do not claim physical x87 accuracy; arithmetic NaNs classify at declared numeric outputs, other words remain exact. No gameplay routine is replaced in the original-instruction oracle.'
fixture={'base':BASE,'memory':'airborne-spin-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
path=out/'airborne-spin-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 airborne spin:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_airborne_spin_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'balance-score-diagnostics.wasm',out/'grounded-update-callbacks.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
