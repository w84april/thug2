"""Full original skater kick with actual script, shadow geometry and audio paths."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-rigidbody-response.py').read_text().split('for name in [0,0x0ca64c41')[0],'<verified response services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind_new(0x42c140,1421,'thug_rigidbody_kick_draft',0,'void',True,True)
bind_new(0x48c770,64,'thug_scene_first_ordinary_draft',0,'word',this=False)
functions['0x48c770']['pointer_result']=True
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
function_exports.append([0x4b4630,'thug_model_geometry_enabled_draft'])
for name,at,n in [('thug_rigidbody_skater_references_draft',0x695150,96),('thug_rigidbody_skater_radii_draft',0x6939b0,32)]:
 for off in range(0,n,4):glob(name,at+off,0,offset=off)
for name,at,value in [('thug_rigidbody_initialization_constant_draft',0x6939d0,bits(77)),('thug_rigidbody_kick_sound_time_draft',0x6939d8,0)]:global_default(name,at,value)
for off in range(0,12,4):
 at=0x690fd4+off
 if at not in index:glob('thug_random_state',at,oracle.word(at),offset=off)
initial=bytes(memory);oracle.initial=initial
rng=random.Random(0x42c140)
class KickGraph(ResponseGraph):
 def __init__(self):
  super().__init__();self.changes={};self.put(RIGID+0x40,'<6f',20,12,1,1,1,1)
  self.put(RIGID+0xc0,'<f',5);self.put(RIGID+0xe0,'<2I',300,80)
  self.put(OBJ+0x14,'<I',crc('kick_fixture'))
  self.scene_chain([0])
 def scene_chain(self,flags):
  tail=self.alloc(16);self.put(tail,'<4I',0,0xffffffff,0,tail);self.scenes=[];head=tail
  for flag in reversed(flags):
   s=self.alloc(0xd8);self.put(s+0x8d,'<B',flag);self.put(s+0xd0,'<2I',self.table([]),0)
   n=self.alloc(16);self.put(n,'<4I',0,s,0,head);head=n;self.scenes.insert(0,s)
  self.changes[0x6fa7ec]=head
 def skater(self,i=7,position=(0,20,30,1),velocity=(40,-4,5,1),radius=20):
  s=self.alloc(0xc0);self.put(s+0x4c,'<4f',*position);self.put(s+0xac,'<4f',*velocity)
  self.changes.update({0x695150+i*12:s,0x6939b0+i*4:bits(radius)});return s
 def shadow(self,collision=True,render=True,instanced=True):
  geom=self.alloc(0x1c);c=self.alloc(0x10);self.put(c+8,'<I',0xaabbccf1)
  r=self.alloc(0x60);vt=self.alloc(56);self.put(vt+52,'<I',0x4b4630);fields.add(vt+52)
  self.put(r,'<I',vt);self.put(r+0x3c,'<2I',0,0);self.put(r+0x4c,'<I',0)
  if instanced:
   inst=self.alloc(100);self.put(inst+0x4c,'<I',0xaabbcc01);self.put(r+0x4c,'<I',inst)
  else:
   arr=self.alloc(12);self.put(r+0x3c,'<2I',arr,3)
   for i in range(3):
    mesh=self.alloc(4);self.put(mesh,'<I',0xffffff40+i);self.put(arr+4*i,'<I',mesh)
  self.put(geom+0x14,'<2I',r if render else 0,c if collision else 0)
  key=crc('kick_fixture_shadow');self.put(self.scenes[0]+0xd0,'<I',self.table([(key,geom)]))
 def kickscript(self,parameters=True):
  calls=self.impactscript(parameters);self.put(RIGID+0xc4,'<I',self.word(RIGID+0xc8));self.put(RIGID+0xc8,'<I',0);return calls
 def kicksound(self,items=()):
  s=self.sound(items);self.put(RIGID+0xd8,'<I',s);self.put(RIGID+0xdc,'<I',0)
 def run(self,label,calls=None):return check(self,calls or [call(0x42c140,RIGID)],label,self.changes)
# Getter's empty, skipped, first-match and exhausted-list paths.
for flags in [[],[0],[1],[255],[1,0],[0,1],[1,2,255],[255,2,0,0]]:
 g=KickGraph();g.scene_chain(flags);steps=g.run('ordinary scene/'+str(flags),[call(0x48c770)])
 assert steps[0]['result']==next((s for s,f in zip(g.scenes,flags) if not f),0)
g=KickGraph();g.run('all eight references null')
for i in range(8):
 for mode in [0,1,2,0xffffffff]:
  g=KickGraph();g.skater(i);g.put(RIGID+0x10c,'<I',mode);g.run(f'reference{i}/mode{mode}')
# Coarse horizontal / vertical gates at and around original boundaries.
for x in [-40.001,-40,-39.999,0,39.999,40,40.001]:
 for y in [-109.001,-109,-108.999,-77.001,-77,-76.999,-.001,0,.001,31.999,32,32.001]:
  g=KickGraph();g.skater(position=(10+x,20+y,30,1));g.run(f'distance gates/{x}/{y}')
for velocity in [(-200,-4,5,1),(3,-4,5,1),(3.005,-3.995,5.005,1),(3.01,-4,5,1),(3.011,-4,5,1),
 (3,-3.99,5,1),(3,-3.989,5,1),(3,-4,5.01,1),(3,-4,5.011,1),(3,-100,5,1),(3,100,5,1)]:
 g=KickGraph();g.skater(7,velocity=velocity);g.skater(0,velocity=(200,0,0,1));g.run('velocity gates/'+str(velocity))
for strength in [0,.01,.011,49.999,50,50.001,99.999,100,100.001,300]:
 for y in [-90,-77,0,10]:
  g=KickGraph();g.skater(position=(0,20+y,30,1),velocity=(3+strength,-4,5,1));g.run(f'strength thresholds/{strength}/{y}')
# Opposed horizontal velocity with vertical strength makes direction sum zero.
for x in [0,10]:
 g=KickGraph();g.skater(position=(x,20,30,1),velocity=(-37,400,5,1));g.run('zero normalizers/'+str(x))
for collision,render,instanced in itertools.product([False,True],repeat=3):
 g=KickGraph();g.skater();g.shadow(collision,render,instanced);g.run(f'shadow/{collision}/{render}/{instanced}')
# Actual script allocation/execution, sound parameter mutation and playback.
for script,sound,params in itertools.product([False,True],repeat=3):
 g=KickGraph();g.skater();calls=g.kickscript(params) if script else []
 if sound:g.kicksound()
 g.shadow();g.run(f'side effects/{script}/{sound}/{params}',calls+[call(0x42c140,RIGID)]*2)
for timer in [0,999,1000,1001,0x800003e8,0xfffffff0]:
 for shared in [False,True]:
  g=KickGraph();g.skater();g.kicksound()
  if shared:g.changes[0x6939d8]=timer
  else:g.put(RIGID+0xf0,'<I',timer)
  g.run(f'signed cooldown/{timer}/{shared}')
g=KickGraph();g.skater();g.put(RIGID+0x19c,'<I',P);g.run('sound component without profile')
for delay in [0,1,99,100,0xffffffff,0x80000000]:
 g=KickGraph();g.skater();g.kicksound();g.put(RIGID+0xe0,'<2I',delay,delay);g.run('wrapped random delay/'+str(delay))
# Wide ranges exercise rounding and finite overflow without class-only NaN masks.
for j in range(128):
 g=KickGraph();g.skater(j%8,position=(rng.uniform(-5,5),rng.uniform(-80,40),rng.uniform(25,35),1),velocity=(*[rng.uniform(-500,500) for _ in range(3)],1))
 for off in [0x110,0x120,0x140]:g.put(RIGID+off,'<4f',*[rng.uniform(-30,30) for _ in range(4)])
 g.put(RIGID+0x40,'<6f',200,100,*[rng.uniform(-2,5) for _ in range(4)]);g.put(RIGID+0x18,'<f',rng.uniform(0,1))
 if j%4==0:g.kicksound()
 g.run('random finite/'+str(j))
for magnitude in [1e-30,1e-20,1e20,1e30,3e38]:
 for offset in [0x18,0x48,0x4c,0x50,0x54]:
  for sign in [1,-1]:
   g=KickGraph();g.skater();g.put(RIGID+offset,'<f',magnitude*sign);g.run(f'finite overflow/{offset:x}/{magnitude}/{sign}')
for first in ['out of range','negative strength','nearly stationary','kick']:
 g=KickGraph();g.skater(0,position=(20,20,30,1),velocity=(-40,-4,5,1))
 g.skater(7,position=(1000 if first=='out of range' else 0,20,30,1),velocity={'negative strength':(-40,-4,5,1),'nearly stationary':(3,-4,5,1)}.get(first,(40,-4,5,1)))
 g.run('two eligible references/'+first)
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',missing,flush=True)
# The shared finish helper requires every instruction to be covered when no
# exclusions are supplied. Both new bodies satisfy that strict requirement.
scope='Full42c140 skater kick and48c770 ordinary-scene getter. Eight reverse references, PC24 arithmetic, activation, real attached scripts, shadow hash lookup and actual4b4630 renderer flag changes, Sound parameters/playback, signed timers and wrapped random delays. Initialized sentinel list with ordinary scene for kick, valid finite gameplay inputs and successful heap; explicit original OS audio boundaries. No game callee substituted. Exact arena/globals/heap/returns; no playable level or full Rigidbody Update claim.'
finish('rigidbody-kick',scope,{},extra)
