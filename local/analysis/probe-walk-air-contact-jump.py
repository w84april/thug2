"""Original contact-jump parent with retained probes, moving owners and QB callbacks."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-transfer.py').read_text().split('\nrecords=[]')[0],'<preserved Walk contacts and events>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x5293f0,1039,'thug_walk_air_contact_jump_draft',0,'void',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
defaults[index[0x7d1ec8]]=0;defaults[index[0x696d60]]=1000
if 0x7ce500 not in index:glob('thug_objective_objects',0x7ce500,0)
required={0x420d18bc:200,0x12333ebd:1000,0x246d0bf3:.5,0x99510695:100,0x9ea1974a:48,0x48c0ac2a:60,0x06ebbab7:12,0xa5e2da58:900}
class ContactJumpGraph(TransferGraph):
 def __init__(self):
  super().__init__(submode=1);self.parameters(overrides=required);self.put(P+0x1788,'<I',STATE);self.put(STATE+0x11c,'<f',100)
  self.put(P+0x24,'<4f',0,0,0,1);self.put(P+0x34,'<4f',7,0,9,1);self.put(P+0x44,'<f',-10);self.put(P+0x94,'<f',1)
  self.put(P+0x84,'<4f',0,0,-1,1);self.put(P+0x1878,'<4f',1,0,0,1);self.put(P+0x48,'<4f',0,0,1,1)
  self.put(INPUT+0x1c0,'<2I',1,500);self.put(P+0x1c,'<I',0);self.put(PHYSICS+0x4e0,'<I',0)
  self.put(OBJ+0x14,'<I',0x100);self.put(ALTOWNER+0x14,'<I',0x101);self.put(EM+8,'<I',self.table([(0x100,OBJ),(0x101,ALTOWNER)]))
  for key in [0xd5349cc6,0x82135dd7,0x4c2b6df3]:self.symbol(key,2,bits(0))
  self.names=[]
  for owner in [OBJ,ALTOWNER]:
   name=self.alloc(0x1bc0);self.image[name-BASE:name-BASE+0x1bc0]=bytes(0x1bc0);self.put(name,'<5I',0,0x270f56e1,0,owner,self.word(owner+0x100));self.put(owner+0x100,'<I',name);self.names.append(name)
  owned=self.alloc(0x40);self.image[owned-BASE:owned-BASE+0x40]=bytes(0x40);table=self.table([]);self.image[owned+0x20-BASE:owned+0x38-BASE]=self.image[table-BASE:table-BASE+24];self.owned=owned
 def contact(self,slot=0,normal=(0,0,1,1),moving='none',event=False):
  contact=P+0xa0+slot*0xcc;probe=contact+0x1c;self.put(contact,'<B',1);self.put(contact+4,'<4f',*normal)
  self.put(probe+0x58,'<I',0x111+slot);self.put(probe+0x6d,'<B',int(event))
  if moving!='none':
   self.put(probe+0xa4,'<I',0x201+slot)
   if moving!='dead':
    owner=self.alloc(0x110);self.image[owner-BASE:owner-BASE+0x110]=bytes(0x110);self.put(owner+4,'<I',probe+0x98);self.put(owner+0x14,'<I',0x201+slot)
    self.put(owner+0xac,'<4f',2,5,-3,1);self.put(probe+0x98,'<3I',owner,0,0)
  return probe
records=[];branches=Counter()
for address in [0x5295d9,0x52968f,0x529685,0x529763,0x529798,0x5297bd,0x5297f1]:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:branches.update([at]),begin=address,end=address)
def run(g,label,repeats=1,changes=None):
 before=dict(branches);stages=g.run([call(0x5293f0,P,[Q])]*repeats,label,{0x7ce500:g.owned,**(changes or {})})
 records.append({'label':label,'callbacks':oracle.word(CBSTATE),'event':oracle.word(P+0x78),'branches':{hex(k):v-before.get(k,0) for k,v in branches.items() if v-before.get(k,0)}})
 return stages
for mask in [0,*[1<<i for i in range(7)],3,0x42,0x7c,0x7f]:
 g=ContactJumpGraph()
 for i in range(7):
  if mask&(1<<i):g.contact(i,normal=(i*.125,0,1,1))
 run(g,'ordered contacts '+str(mask),2)
for normal,direction,amount in itertools.product([(0,0,1,1),(1,0,0,0),(0,1,0,-1),(.5,0,.5,2)],[(0,0,-1,1),(0,0,1,1),(-1,0,0,-2)],[0,1]):
 g=ContactJumpGraph();g.contact(normal=normal);g.put(P+0x84,'<4f',*direction);g.put(P+0x94,'<f',amount);run(g,f'reflection {normal}/{direction}/{amount}')
for pressed,speed in itertools.product([0,1,255],[-10,0,.00001,float('nan')]):
 g=ContactJumpGraph();g.contact();g.put(INPUT+0x1c0,'<B',pressed);g.put(P+0x44,'<f',speed);run(g,f'input/vertical gate {pressed}/{speed}')
for key in [0xd5349cc6,0x82135dd7,0x4c2b6df3]:
 for v in [99,100,101,999,1000,1001,2147483648,float('nan')]:
  g=ContactJumpGraph();g.contact();g.symbol(key,2,bits(v));run(g,f'cooldown/height {key:x}/{v}')
for age,duration,minimum in itertools.product([0,1,500,1000,1001,0xffffffff],[0,1000],[0,.5,1]):
 g=ContactJumpGraph();g.contact();g.parameters(overrides={**required,0x12333ebd:duration,0x246d0bf3:minimum});g.put(INPUT+0x1c4,'<I',(1000-age)&0xffffffff);run(g,f'held duration {age}/{duration}/{minimum}')
for moving in ['none','dead','live']:
 for notified in [0,1]:
  g=ContactJumpGraph();g.contact(moving=moving);g.put(g.names[0]+0x13b0,'<B',notified);run(g,f'moving momentum and notification {moving}/{notified}',2)
for mutation in ['observe','cancel','owner','velocity','physics','checksum']:
 for moving in ['none','live']:
  g=ContactJumpGraph();probe=g.contact(moving=moving,event=True);g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(0x201,[])])
  alternate=g.alloc(0x1550);g.image[alternate-BASE:alternate-BASE+0x1550]=g.image[PHYSICS-BASE:PHYSICS-BASE+0x1550]
  writes={'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'owner':[(P+12,ALTOWNER)],'velocity':[(P+0x44,bits(-22))],'physics':[(P+0x178c,alternate)],'checksum':[(probe+0x58,0x222)]}[mutation];g.callback(writes)
  run(g,f'collision script {moving}/{mutation}');assert oracle.word(CBSTATE)>0
for gravity,height,wide in itertools.product([100,900],[49,60],[False,True]):
 g=ContactJumpGraph();g.contact();g.parameters(overrides={**required,0xa5e2da58:gravity});g.plane(height,moving=False,up=False,half=128 if wide else 8);run(g,f'connected lip clearance {gravity}/{height}/{wide}')
scope='Candidate complete contact-jump parent5293f0 with seven-contact priority, reflected directions, held-input scaling, live/dead moving references, ballistic lip clearance, collision QB callbacks and callback-sensitive notifications/timestamps. Full airborne frames and playable training remain unfinished.'
extra={**extra,'native_callbacks':[{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-air-contact-jump',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-contact-jump-original.json').read_text());report['records']=records;report['branch_hits']={hex(k):v for k,v in branches.items()}
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-contact-jump-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-contact-jump-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
