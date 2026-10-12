"""Original Walk ground helpers and an explicitly interrupted ground parent."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
exec(compile(source,'<preserved Walk setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x52a620,215,'thug_walk_follow_platform_draft',0,'void',True,False,True),
 (0x5277b0,281,'thug_walk_prepare_cache_draft',0,'void',False,False,True),
 (0x526260,464,'thug_walk_face_velocity_draft',0,'void',False,False,True),
 (0x528120,253,'thug_walk_target_speed_draft',0,'double',False,False,True),
 (0x526430,191,'thug_walk_slope_speed_draft',2,'double',False,False,True),
 (0x528950,2058,'thug_walk_accelerate_draft',1,'void',False,False,True),
 (0x5264f0,857,'thug_walk_step_height_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
functions[hex(0x526430)]['float_args']=[0]
bind(0x52d300,'thug_walk_ground_prefix_draft',0,'void',True,True)
GATE,CONTACT,PLATFORM=P+0x7000,P+0x7400,P+0x7800
class GroundGraph(WalkGraph):
 def __init__(self):
  super().__init__()
  for a,n in [(GATE,0x80),(CONTACT,0xb0),(PLATFORM,0x110)]:self.image[a-BASE:a-BASE+n]=bytes(n)
  self.put(P+0x1784,'<I',GATE);self.put(GATE+0x18,'<I',CONTACT)
  self.put(CONTACT,'<3I',PLATFORM,0,0);self.put(PLATFORM+4,'<I',CONTACT)
  self.put(CONTACT+0xc,'<16f',*IDENTITY);self.put(CONTACT+0x4c,'<4f',1,2,3,1)
  self.put(PLATFORM+0x6c,'<16f',*IDENTITY);self.put(PLATFORM+0x4c,'<4f',1,2,3,1)
  self.parameters()
 def parameters(self,threshold=2,fast=6,rate=4,radius=4,above=6,below=8,overrides=None):
  params={0x0515a933:threshold,0xe6c1cd0d:fast,0x7a583b9b:rate,0x99978d2b:radius,0x9ea1974a:above,0xaf3e4251:below,
   0xc1528f7f:.4,0x79d182ad:20,0x7213ef07:100,0xcc461b87:40,0x8afb8788:1,0xdb05e84e:30,0xb557804b:180,
   0x7b446c98:.5,0xe0456382:.25,0x6da7f696:2,0x6cb2e5de:10,0xa26760f5:4,0xacfa4e0c:5,0x0a2aa811:10,0x4f47c998:50,0x6590a49b:20,0x11edcc52:10,0xcee3a3e1:8,0x227d72ee:2,0x856a80d3:4,0x8e1cf27a:1}
  params.update(overrides or {});self.symbol(0x6775e538,10,self.structure([(k,2,bits(v)) for k,v in params.items()]))
 def wall(self,z=2,moving=False):
  actor,owner=self.plane(0,moving=moving,half=32)
  geo=self.word(actor+12);verts=self.word(geo+48)
  self.put(verts,'<9f',-32,-32,z,32,-32,z,0,32,z)
  self.put(geo+16,'<8f',-32,-32,z,1,32,32,z,1)
  return actor,owner
for kind in ['absent','dead','still','translated','rotated Y','rotated X']:
 for forward in [(2,0,3,1),(0,1,0,1),(0,0,0,1)]:
  g=GroundGraph();g.put(P+0x48,'<4f',*forward)
  if kind=='absent':g.put(GATE+0x18,'<I',0)
  if kind=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
  if kind=='translated':g.put(PLATFORM+0x4c,'<4f',11,22,33,1)
  if kind=='rotated Y':g.put(PLATFORM+0x6c,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,0,0,0,1)
  if kind=='rotated X':g.put(PLATFORM+0x6c,'<16f',1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1)
  g.run([call(0x52a620,P)]*2,f'follow platform/{kind}/{forward}')
for kind in ['empty','static','moving','both','far','masked']:
 g=GroundGraph();g.put(OBJ+0x4c,'<4f',0,0,0,1)
 if kind!='empty':g.plane(0 if kind!='far' else 100,moving=False)
 if kind in ['moving','both','masked']:g.plane(0,moving=True,flags=6 if kind=='masked' else 0)
 g.run([call(0x5277b0,P)]*2,f'prepare cache/{kind}')
for speed,dt,rate in itertools.product([0,1,2,3,6,10],[-.1,0,.1,1],[0,4]):
 g=GroundGraph();g.parameters(rate=rate);g.put(P+0x34,'<4f',speed,0,0,1);g.put(P+0x48,'<4f',0,0,1,1);g.put(P+0x80,'<f',dt)
 g.run([call(0x526260,P)]*2,f'face velocity/{speed}/{dt}/{rate}')
for input_,factor,flag in itertools.product([0,.1,.3,.4,.5,1,2,-1],[-1,0,.5,1,2],[0,1]):
 g=GroundGraph();g.put(P+0x94,'<f',input_);g.put(P+0x1868,'<f',factor);g.put(P+0x17a4,'<B',flag)
 g.run([call(0x528120,P)]*2,f'target speed/{input_}/{factor}/{flag}')
for normal,speed,direction in itertools.product([(0,1,0,1),(0,.95,0,1),(1,.5,0,1),(1,-1,2,1)],[0,10,20,30,100],[(0,0,0,1),(1,0,0,1),(0,1,0,1),(0,0,1,1),(.6,0,.8,1)]):
 g=GroundGraph();g.put(P+0x1794,'<4f',*normal);g.put(P+0x84,'<4f',*direction)
 g.run([call(0x526430,P,[bits(speed),P+0x84])]*2,f'slope speed/{normal}/{speed}/{direction}')
# Real steering paths with synthetic but finite game state and actual geometry.
for velocity,facing,input_dir,amount,latched in itertools.product([(0,0,0,1),(1,0,0,1),(3,0,4,1),(40,0,0,1)],[(1,0,0,1),(0,0,1,1)],[(1,0,0,1),(0,0,1,1),(-1,0,0,1)],[0,.4,1],[0,1]):
 g=GroundGraph();g.put(P+0x34,'<4f',*velocity);g.put(P+0x48,'<4f',*facing);g.put(P+0x84,'<4f',*input_dir);g.put(P+0x94,'<f',amount);g.put(P+0x186c,'<B',latched);g.put(P+0x1798,'<f',1)
 g.run([call(0x528950,P,[P+0x34,Q])]*2,f'accelerate/{velocity}/{facing}/{input_dir}/{amount}/{latched}')
for kind in ['wall','behind','cached moving']:
 g=GroundGraph();g.put(P+0x24,'<4f',0,0,0,1);g.put(P+0x34,'<4f',30,0,0,1);g.put(P+0x48,'<4f',0,0,1,1);g.put(P+0x84,'<4f',1,0,0,1);g.put(P+0x94,'<f',1);g.put(P+0x1798,'<f',1)
 if kind=='cached moving':g.plane(-100,moving=False);g.wall(moving=True);g.put(OBJ+0x4c,'<4f',0,0,0,1)
 else:g.wall(z=-2 if kind=='behind' else 2)
 calls=([call(0x5277b0,P)] if kind=='cached moving' else [])+[call(0x528950,P,[P+0x34,Q])]*2
 g.run(calls,'sharp turn collision/'+kind)
for facing,dt in itertools.product([(2,0,0,1),(-2,0,0,1),(0,0,2,1)],[0,30]):
 g=GroundGraph();g.put(P+0x34,'<4f',20,0,0,1);g.put(P+0x48,'<4f',*facing);g.put(P+0x84,'<4f',*facing);g.put(P+0x94,'<f',1);g.put(P+0x1798,'<f',1)
 g.run([call(0x528950,P,[P+0x34,Q])],'steering clamp/'+str((facing,dt)),{0x684fc8:bits(dt)})
for kind,offset,input_,speed in itertools.product(['empty','wall','step','moving step'],[0,.5],[0,1],[0,4]):
 g=GroundGraph();g.put(P+0x24,'<4f',0,0,0,1);g.put(P+0x48,'<4f',0,0,1,1);g.put(P+0x1794,'<4f',0,1,0,0);g.put(P+0x714,'<f',offset);g.put(P+0x94,'<f',input_);g.put(P+0x34,'<4f',speed,0,0,1);g.put(P+0x80,'<f',.1)
 if kind!='empty':g.wall()
 if kind in ['step','moving step']:g.plane(1,moving=kind=='moving step')
 g.run([call(0x5264f0,P,[Q])]*2,f'step height/{kind}/{offset}/{input_}/{speed}')
for direction in [(0,-1,1,1),(0,0,0,1),(1,2,3,1),(.0001,-1,.0001,2)]:
 g=GroundGraph();g.put(P+0x48,'<4f',*direction);g.put(P+0x1794,'<4f',0,0,0,1)
 g.run([call(0x5264f0,P,[Q])]*2,'step direction/'+str(direction))
rng=random.Random(0x528950)
for i in range(32):
 g=GroundGraph()
 for at in [P+0x34,P+0x48,P+0x84]:g.put(at,'<4f',rng.uniform(-8,8),0,rng.uniform(-8,8),1)
 g.put(P+0x94,'<f',rng.choice([.31,.4,.73,1]));g.put(P+0x1794,'<4f',1,.5,2,1);g.put(P+0x186c,'<B',i%2)
 g.run([call(0x528950,P,[P+0x34,Q])]*2,f'steering finite vectors/{i}')
# Explicitly stop before the first unresolved ground-state transition routine.
ground_hits=Counter();ground_active=False
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:ground_hits.update([at]),begin=0x52d300,end=0x52d4ae)
def ground_boundary(cpu,at,size,user):
 if ground_active:cpu.mem_write(BOUNDARY,struct.pack('<4I',at,0,P,1));cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,ground_boundary,begin=0x52c2c0,end=0x52c2c0)
prefix_records=[]
for moving,amount,turn in itertools.product([False,True],[0,.4,1],[False,True]):
 g=GroundGraph();g.put(P+0x24,'<4f',0,0,0,1);g.put(OBJ+0x4c,'<4f',0,0,0,1);g.put(P+0x34,'<4f',30,0,0,1);g.put(P+0x48,'<4f',0,0,1,1);g.put(P+0x84,'<4f',1 if turn else 0,0,0 if turn else 1,1);g.put(P+0x94,'<f',amount);g.put(P+0x1798,'<f',1)
 if moving:g.put(PLATFORM+0x4c,'<4f',2,3,4,1)
 else:g.put(GATE+0x18,'<I',0)
 g.wall();stages=g.run([],f'ground frame prefix/{moving}/{amount}/{turn}');cpu=oracle.cpu;before=bytes(cpu.mem_read(BASE,len(initial)));sp=oracle.stack+0x18000
 cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,P);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 ground_active=True
 try:cpu.emu_start(0x52d300,oracle.stop,count=1000000)
 finally:ground_active=False
 assert cpu.reg_read(UC_X86_REG_EIP)==0x52c2c0 and oracle.word(BOUNDARY)==0x52c2c0
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x52d300','this':P,'args':[Q,DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True,'boundary_factory':0x52c2c0})
 oracle.counts['thug_walk_ground_prefix_draft']+=1;prefix_records.append({'moving':moving,'amount':amount,'turn':turn,'boundary':'0x52c2c0'})
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x52c2c0}
scope='Seven complete original Walk routines recover platform motion, collision-cache preparation, velocity-facing interpolation, analog target speed, slope attenuation, acceleration/steering and two-probe step height. Real collision geometry, reference lifetimes and QB/math callees execute. Whole arena/globals and completed-call preserved registers compare. The ground parent executes platform follow, cache preparation and acceleration in original order, then explicitly stops before transition routine52c2c0; the parent is not counted as recovered. Initialized single-threaded graphs, finite numeric fixtures and required QB parameters are contracts. Ten unexercised instructions have documented unreachable-path proofs under these contracts. Remaining ground transitions, full movement/startup, rendering and playable training remain unfinished.'
saved=coverage.copy();coverage.clear();finish('walk-ground',scope,{},extra);coverage.update(saved)
p=folder/'walk-ground-original.json';report=json.loads(p.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
exclusions=json.loads((folder/'walk-ground-exclusions.json').read_text())
for at,row in report['instruction_coverage'].items():
 row['excluded']=exclusions.get(at,{})
 assert set(row['missing'])==set(row['excluded']),(at,row)
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d300,431),0x52d300))
report['partial_ground']={'address':'0x52d300','covered':sum(bool(ground_hits[i.address]) for i in code),'total':len(code),'interrupted_calls':len(prefix_records),'records':prefix_records}
p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['instruction_coverage']))

(folder/'walk-ground-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
