"""Complete contact constraints, collision response and impact side effects."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-prop-sound.py').read_text().split('# Exact arithmetic, boundary selection and input/output aliasing.')[0],'<preserved Sound/heap/script comparison services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
RIGID=BASE+0xc0000
specs=[(0x42cee0,175,'rigidbody_contact_inverse',2,'double',False,False,True),
 (0x42cf90,1312,'rigidbody_constraints',0,'void',False,False,True),
 (0x430be0,523,'rigidbody_response',1,'void',True,True,True),
 (0x42e980,399,'rigidbody_impact',2,'void',True,True,True),
 (0x433240,573,'object_sound_parameters',1,'void',False,False,True),
 (0x47afe0,31,'sound_active_count',0,'word',False,False,True),
 (0x47ac10,55,'sound_curve',1,'word',False,False,False),
 (0x4680e0,60,'sound_volume_find',1,'word',False,False,False),
 (0x48d090,3,'sound_notification',3,'void',False,False,True)]
for a,n,name,nargs,result,heap,diag,this in specs:bind_new(a,n,'thug_'+name+'_draft',nargs,result,heap,diag,this)
functions['0x42e980']['float_args']=[0];functions['0x48d090']['float_args']=[1,2]
functions['0x4680e0']['pointer_result']=True
function_exports.append([0x48d090,'thug_sound_notification_draft'])
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
for offset in range(0,32,4):glob('thug_rigidbody_rotated_contacts_draft',0x695130+offset,0,offset=offset)
initial=bytes(memory);oracle.initial=initial
rng=random.Random(0x430be0)
class ResponseGraph(SoundGraph):
 def __init__(self):
  super().__init__();self.image[RIGID-BASE:RIGID-BASE+0x1a0]=bytes(0x1a0)
  self.put(RIGID+12,'<I',OBJ);self.put(RIGID+0x18,'<f',.003)
  self.put(RIGID+0x2c,'<3f',.4,.5,10)
  self.put(RIGID+0x110,'<4f',10,20,30,1);self.put(RIGID+0x120,'<4f',3,-4,5,1);self.put(RIGID+0x140,'<4f',.2,.3,-.4,1)
  self.put(RIGID+0xe8,'<2f',20,300)
  vt=self.alloc(56);self.put(vt+52,'<I',0x48d090);fields.add(vt+52);self.put(P,'<I',vt)
  self.put(P+0x18,'<9I',0x12345678,0,0,0,0,0,0,0,0x12345678)
  self.tableptr=self.table([])
 def constraints(self,n,active=3):
  c=self.alloc(max(n,1)*36);self.put(RIGID+0x98,'<IH',c,n)
  changes={0x6f2260:self.tableptr}
  for i in range(n):
   vals=[rng.uniform(-10,10) for _ in range(4)];self.put(c+i*36,'<8fB',*vals,*[rng.uniform(-40,40) for _ in range(4)],int(bool(active&(1<<i))))
   changes.update({0x695130+i*16+j*4:bits(vals[j]) for j in range(4)})
  return c,changes
 def impactscript(self,parameters=True):
  key=0x71663311;code=self.alloc(8);self.put(code,'<2B',1,0x24);entry=self.alloc(20);self.put(entry,'<5I',key,code,1,0,0)
  blob=self.alloc(20);self.put(blob,'<3I2B',0,2,2,1,0x24);self.symbol(key,7,blob)
  self.put(CACHE+20,'<4I',self.table([(key,entry)]),0,0,0);self.put(RIGID+0xc8,'<I',key)
  self.put(RIGID+0xd4,'<I',self.structure([(123,1,456),(124,6,self.vector([bits(v) for v in [1,2,3]])),(0x43f454d0,6,self.vector([bits(v) for v in [-1,-2,-3]]))]) if parameters else 0)
  return [call(0x45e510,OBJ)]
 def sound(self,items=()):
  s=self.structure([(0,13,0x12345678),*items]);self.put(RIGID+0x19c,'<I',P);self.put(RIGID+0xdc,'<I',s);return s
 def collision(self,n=(0,1,0,0)):
  f=self.alloc(0xcc);self.put(f+0x78,'<4f',5,6,7,1);self.put(f+0x88,'<4f',*n);return f
for name in [0,0x0ca64c41,0x9706104b,0xef082878,0xf221474c,0xffffffff,0xf0000000]:
 check(ResponseGraph(),[call(0x47ac10,args=[name])],f'curve/{name:x}')
for count in [0,1,12,35,36,37,48]:
 for active in [1,2,0xff]:
  g=ResponseGraph();changes={0x6f85d8+i*24:active if i<count else 0 for i in range(48)}
  check(g,[call(0x47afe0,CONFIG)],f'active slots/{count}/{active}',changes)
for kind in ['empty','found','collision','null duplicate','missing']:
 g=ResponseGraph();wanted=g.volume();key=0x12345678;t=g.table([] if kind=='empty' else [(key,wanted)])
 bucket=g.word(t+4)+(key&((1<<g.word(t))-1))*12
 if kind in ['collision','null duplicate']:
  chain=g.alloc(12);g.put(chain,'<3I',key,wanted,0);g.put(bucket,'<3I',key if kind=='null duplicate' else key^0x1000,0,chain)
 check(g,[call(0x4680e0,args=[key^0x1000 if kind=='missing' else key])],f'volume table/{kind}',{0x6f2260:t})
check(ResponseGraph(),[call(0x48d090,P,[123,bits(50),bits(25)])],'original sound virtual')
# Effective contact mass and the entire two-contact solver, finite exact bits.
for mass in [0,.003,1,-.01,1e-30,1e20]:
 for scale in [0,1,1e-20,1e20]:
  for j in range(3):
   g=ResponseGraph();g.put(RIGID+0x18,'<f',mass);n=g.vec([rng.uniform(-2,2)*scale for _ in range(4)]);v=g.vec([rng.uniform(-20,20) for _ in range(4)])
   # Nonzero normal avoids the original undefined zero-direction divide.
   if scale==0:g.put(n,'<4f',1,0,0,1)
   check(g,[call(0x42cee0,RIGID,[n,v])],f'effective mass/{mass}/{scale}/{j}')
for n in [0,1,2]:
 for mask in range(4):
  for speed in [0,.099,.1,.101,1,100]:
   g=ResponseGraph();c,changes=g.constraints(n,mask);g.put(RIGID+0x120,'<4f',speed,0,0,1);g.put(RIGID+0x140,'<4f',0,0,0,1)
   check(g,[call(0x42cf90,RIGID)]*2,f'constraints/count{n}/active{mask}/speed{speed}',changes)
for scale in [0,.003,1,-.01,1e-25,1e25]:
 for dt in [0,1,-.5]:
  for j in range(4):
   g=ResponseGraph();c,changes=g.constraints(2);g.put(RIGID+0x18,'<f',scale);g.put(RIGID+0x34,'<f',j*5)
   for offset in [0x110,0x120,0x140]:g.put(RIGID+offset,'<4f',*[rng.uniform(-100,100) for _ in range(4)])
   changes[0x684fc8]=bits(dt)
   check(g,[call(0x42cf90,RIGID)],f'constraints/random/{scale}/{dt}/{j}',changes)
# Coincident anchors exercise the zero-distance positional-correction branch.
g=ResponseGraph();c,ch=g.constraints(2);g.put(RIGID+0x110,'<4f',0,0,0,0)
for i in range(2):g.put(c+i*36+16,'<4I',*[ch[0x695130+i*16+j*4] for j in range(4)])
check(g,[call(0x42cf90,RIGID)],'constraints coincident targets',ch)
# Direct sound parameter path: real playback, queueing, all optional parameters.
for slot in [None,-1,0,1,8,9]:
 for named in [False,True]:
  for strength in [None,0,50,100,200]:
   g=ResponseGraph();items=[] if not named else [(0,13,0x12345678)]
   if slot is not None:items.append((0x7321a8d6,1,slot&0xffffffff))
   if strength is not None:items.append((0x9e497fc6,2,bits(strength)))
   s=g.structure(items);check(g,[call(0x433240,P,[s])],f'sound fallback/{slot}/{named}/{strength}')
for strength in [None,-25,25,100,150]:
 for curve in [0x0ca64c41,0x9706104b,0xef082878,0xf221474c]:
  for detached in [False,True]:
   g=ResponseGraph();vol=g.volume();t=g.table([(123,vol)])
   items=[(0,13,0x12345678),(0xf6a36814,2,bits(20)),(0xd8604126,2,bits(120)),(0xff2020ec,2,bits(40)),(0x0c6ac50a,13,curve),(0x8a7132ce,13,123)]
   if detached:items.append((0,13,0xbb39837f))
   if strength is not None:items += [(0x9e497fc6,2,bits(strength))]+[(key,2,bits(v)) for key,v in [(0x0693daaf,80),(0x4391992d,15),(0xfa3e14c5,140),(0x1c5ebb24,90)]]
   check(g,[call(0x433240,P,[g.structure(items)])],f'all sound parameters/{strength}/{curve:x}/{detached}',{0x6f2260:t})
for camera in [False,True]:
 g=ResponseGraph();g.put(P+0x98,'<4f',50000,0,0,1)
 if not camera:g.put(VIEW+24,'<I',0)
 check(g,[call(0x433240,P,[g.structure([(0,13,0x12345678)])])],'silent queue/'+str(camera))
for sound in [False,True]:
 for script in [False,True]:
  for params in [False,True]:
   for speed in [19,20,21,150,300,1000]:
    g=ResponseGraph();calls=g.impactscript(params) if script else [];position=g.vec([1,2,3,9]);g.sound() if sound else None
    check(g,calls+[call(0x42e980,RIGID,[bits(speed),position])]*2,f'impact gates/{sound}/{script}/{params}/{speed}')
for active in [35,36,37,48]:
 g=ResponseGraph();g.sound();position=g.vec([1,2,3,1]);changes={0x6f85d8+i*24:1 if i<active else 0 for i in range(48)}
 check(g,[call(0x42e980,RIGID,[bits(50),position])],f'impact occupancy/{active}',changes)
g=ResponseGraph();g.put(RIGID+0x19c,'<I',P);check(g,[call(0x42e980,RIGID,[bits(50),g.vec([0,0,0,1])])],'impact missing sound profile')
for normal in [(0,1,0,0),(1,0,0,1),(0,0,1,0),(.6,.8,0,1)]:
 for friction in [0,.1,.5,100]:
  for speed in [0,.0001,.001,.01,1,100]:
   g=ResponseGraph();f=g.collision(normal);g.put(RIGID+0x120,'<4f',speed,-speed,speed/2,1);g.put(RIGID+0x30,'<f',friction)
   check(g,[call(0x430be0,RIGID,[f])]*2,f'response/{normal}/{friction}/{speed}')
for i in range(36):
 g=ResponseGraph();f=g.collision([rng.uniform(-1,1) for _ in range(4)]);g.put(RIGID+0x120,'<4f',*[rng.uniform(-500,500) for _ in range(4)]);g.put(RIGID+0x2c,'<2f',rng.uniform(-1,2),rng.uniform(0,3))
 calls=g.impactscript() if i%3==0 else [];g.sound() if i%2==0 else None
 check(g,calls+[call(0x430be0,RIGID,[f])],f'response all side effects/{i}')
print('MISSING',json.dumps({hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()}),flush=True)
scope='Nine complete original contact/impact/Sound routines. Full attached-contact iteration and correction, effective contact mass, collision response/friction and real impact scripts/parameter allocation and audio playback. Initialized successful allocator, fixed pools disabled, disjoint bounded two-contact arrays and finite gameplay inputs; original OS audio boundaries logged explicitly. Exact memory and globals, no substituted game callees. Full Rigidbody Update430e20 and scene frame remain unfinished; no playable claim.'
excluded={hex(a):reason for addresses,reason in [([0x42e9cd,0x42e9d2],'fixed structure pools disabled'),([0x42e9d4,0x42e9d9,0x42e9db,0x42e9dd],'initialized allocator contract'),([0x42ea0e],'successful allocation contract'),([0x42d2aa],'unreachable alignment padding')] for a in addresses}
# Filled after inspecting exact coverage; no arithmetic or game-state masking.
# Original ST0 was recorded by FSTP-double. Compare those same bits via i64,
# avoiding JavaScript NaN canonicalization without changing the arithmetic.
functions['0x42cee0']['name']='thug_rigidbody_contact_inverse_bits_draft'
functions['0x42cee0']['result']='wide'
for c in oracle.cases:
 for step in c['steps']:
  if step['fn']=='0x42cee0':step['result']=str(int.from_bytes(bytes.fromhex(step['result']),'little'))
oracle.counts['thug_rigidbody_contact_inverse_bits_draft']=oracle.counts.pop('thug_rigidbody_contact_inverse_draft')
finish('rigidbody-response',scope,excluded,extra)
