"""Original ledge-jump scan, real collision cache and live script callback cases."""
from pathlib import Path
import math
from unicorn import UC_HOOK_MEM_WRITE
source=Path('local/analysis/probe-walk-transition.py').read_text().split('for flag_index,enabled,gravity')[0]
exec(compile(source,'<preserved Walk transition graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x52bc70,1545,'thug_walk_ledge_jump_draft',0,'byte',True,True,True),
 (0x52c2c0,3107,'thug_walk_resolve_contacts_draft',0,'byte',True,True,True)]
for row in specs:bind_new(*row)
bind(0x52d300,'thug_walk_ground_contacts_prefix_draft',0,'void',True,True)
# Reuse the pinned terminal QB observer and graph builders. The observer is a
# fixture-native callback, not a substitute for collision, event or script code.
source=Path('local/analysis/probe-trigger.py').read_text()
exec(compile(source[source.index('RECORDS,EVENTS,CBSTATE'):source.index('for flags in [0,1,2,3')],'<preserved terminal Trigger callback>','exec'))
TRIGGER,CONTROL=P+0xd000,P+0xd100
for at in [0x434bf0,0x434a60,0x460a20,0x4607a0,0x40ab40,0x40ab50,0x40aba0,0x528220,0x5284c0,0x5260e0,0x52ab90]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
for i in range(8):
 if 0x6918ec+i*4 not in index:glob('thug_collision_cache_registry',0x6918ec+i*4,0,offset=i*4)
if 0x69190c not in index:glob('thug_collision_cache_mask',0x69190c)
stack_records=[];root_records=[];ledge_active=False;parent_probe=0;root_kind=0;undefined_words=set();source_undefined=set();undefined_provenance={};copy_destination=0

def ledge_observe(cpu,at,size,user):
 global ledge_active,parent_probe,root_kind,source_undefined,copy_destination
 if at in [0x52bc70,0x52c2c0,0x52d300]:
  if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:
   root_kind=at;parent_probe=0;stack_records.append([]);root_records.append({'stack_pointer_fields':[]})
  if at==0x52bc70:ledge_active=True
 elif at in [0x52bcbc,0x52c278,0x52cee2]:
  if at in [0x52bcbc,0x52c278]:ledge_active=False
  if (root_kind==0x52bc70 and at!=0x52cee2) or (root_kind==0x52c2c0 and at==0x52cee2):
   root_records[-1]['indeterminate_words']=sorted(undefined_words);root_records[-1]['indeterminate_provenance']=[undefined_provenance[a] for a in sorted(undefined_words)]
  if at==0x52cee2:parent_probe=0
 elif at==0x417760:
  if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==0x52c32e:parent_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
 elif at==0x43a930:
  source_=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);copy_destination=0
  if source_==parent_probe:
   destination=cpu.reg_read(UC_X86_REG_ECX);copy_destination=destination;field=destination+0x64;fields.add(field)
   root_records[-1]['stack_pointer_fields'].append({'original':source_,'field':field,'size':0xb0})
 elif at==0x43aa26:copy_destination=0
 elif ledge_active:
  ptr_=cpu.reg_read(UC_X86_REG_ECX);count=oracle.word(ptr_+0xfc0);assert count<=500
  assert oracle.stack<=ptr_<oracle.stack+0x20000
  slots=[i for i in range(8) if oracle.word(0x6918ec+i*4)==ptr_ and oracle.word(0x69190c)&(1<<i)]
  assert len(slots)==1,slots
  stack_records[-1].append({'original':ptr_,'global':['thug_collision_cache_registry',slots[0]*4],'mask':['thug_collision_cache_mask',slots[0],0],'size':0xfcc,
   'blocks':[[0,bytes(cpu.mem_read(ptr_,32)).hex()],[0xfc0,bytes(cpu.mem_read(ptr_+0xfc0,12)).hex()],[32,bytes(cpu.mem_read(ptr_+32,count*8)).hex(),list(range(0,count*8,4))]]})
for at in [0x52bc70,0x52c2c0,0x52d300,0x52bcbc,0x52c278,0x52cee2,0x40ab40,0x417760,0x43a930,0x43aa26]:oracle.cpu.hook_add(UC_HOOK_CODE,ledge_observe,begin=at,end=at)
# Track each source field from the probe's initialization. unknown_a8 must
# never be written; scene remains undefined only until an uncached query sets
# it. Exact copier instructions propagate those states, and later writes clear
# destination allowances. No original instruction or data write is replaced.
def ledge_write(cpu,access,address,size,value,user):
 if parent_probe:
  for offset in list(source_undefined):
   if address<parent_probe+offset+4 and address+size>parent_probe+offset:
    assert offset!=0xa8,('Unexpected definition of probe unknown_a8',hex(cpu.reg_read(UC_X86_REG_EIP)))
    source_undefined.remove(offset)
 for at in list(undefined_words):
  if address<at+4 and address+size>at:undefined_words.remove(at);undefined_provenance.pop(at)
 pc=cpu.reg_read(UC_X86_REG_EIP);offset=0xa8 if pc==0x43aa0f else 0x70 if pc==0x4f81f1 else None
 if parent_probe and copy_destination and offset in source_undefined and address==copy_destination+offset:
  assert size==4
  if offset==0xa8:assert cpu.reg_read(UC_X86_REG_EDI)==parent_probe and address==cpu.reg_read(UC_X86_REG_ESI)+0xa8
  undefined_words.add(address);undefined_provenance[address]={'destination':address,'source_probe':parent_probe,'source_offset':offset,'copy_instruction':hex(pc),'source_writes_before_copy':0}
oracle.cpu.hook_add(UC_HOOK_MEM_WRITE,ledge_write)
ledge_base_case=case

def case(calls,patches=(),changes=None,label='Walk ledge'):
 stack_records.clear();root_records.clear();undefined_words.clear();undefined_provenance.clear();stages=ledge_base_case(calls,patches,changes,label)
 assert len(stages)==len(stack_records)==len(root_records)
 for stage,objects,metadata in zip(stages,stack_records,root_records):stage['stack_objects']=objects;stage.update(metadata)
 return stages

class LedgeGraph(TransitionGraph):
 cached=TriggerGraph.cached
 level_nodes=TriggerGraph.level_nodes
 callback=TriggerGraph.callback
 def __init__(self):
  super().__init__();self.parameters(overrides={0xa5e2da58:900,0xac96d24b:.175,0xda85f5ae:18,0x6da7f696:2,0x78e6a5ec:45,0x72660978:2,0x5296e3fd:40,0x76bf49e0:12,0x35b3bbda:6,0x456f216d:45,0x0eecd255:100,0xa2735dd9:50,0xc4c164e8:200,0x38d36700:200,0x4d16f37d:5,0xa20c43b7:.5,0x0bd6a05d:4})
  self.put(P+0x24,'<4f',0,0,0,1);self.put(P+0x48,'<4f',0,0,1,1);self.put(P+0x84,'<4f',0,0,1,1);self.put(P+0x34,'<4f',0,0,3,1)
  self.put(P+0x177c,'<I',TRIGGER);self.put(P+0x1780,'<I',CONTROL)
  self.image[TRIGGER-BASE:CONTROL-BASE+0x80]=bytes(CONTROL-TRIGGER+0x80)
  self.put(TRIGGER,'<6I',0x646648,0xe594f0a2,0,OBJ,0,0);fields.add(TRIGGER)
  self.image[RECORDS-BASE:ALTOWNER-BASE+0x324]=bytes(ALTOWNER-RECORDS+0x324)
  self.put(ALTOWNER,'<I',0x647650);fields.add(ALTOWNER);self.put(ALTOWNER+0x14,'<I',0x101);self.put(ALTOWNER+0x4c,'<4f',7,8,9,1)
  self.cached(5);self.rail_nodes(0);self.plane(-100,moving=False)
 def contact(self,index,active=1,flags=0,clear=0,normal=(0,0,-1)):
  at=P+index*0xcc;self.put(at+0xa0,'<B',active);self.put(at+0xa4,'<3f',*normal);self.put(at+0xb4,'<B',clear);self.put(at+0x10c,'<H',flags)
 def obstacle(self,top=12,z=4,moving=False):
  actor,owner=self.wall(z=z,moving=moving);geo=self.word(actor+12);verts=self.word(geo+48)
  self.put(verts,'<9f',-32,-32,z,32,-32,z,0,top,z);self.put(geo+16,'<8f',-32,-32,z,1,32,top,z,1)
  return actor,owner
 def trigger(self,mutation='observe'):
  self.put(P+0x1864,'<B',1);self.put(P+0x17b4+0x6d,'<B',1);self.put(P+0x17b4+0x58,'<I',0x111)
  self.level_nodes([(0x111,[(0x2ca8a299,13,6)])])
  writes={'observe':[],'cancel':[(CONTROL+0x24,0x10000)],'face':[(P+0x48,bits(2))],'position':[(P+0x28,bits(50))],'owner':[(P+12,ALTOWNER)],'velocity':[(P+0x34,bits(7)),(P+0x44,bits(99))],'trigger owner':[(TRIGGER+12,ALTOWNER)]}[mutation]
  self.callback(writes)

for blocked in [1,2,255]:
 g=LedgeGraph();g.put(STATE+0x70,'<B',blocked);g.run([call(0x52bc70,P,[Q])]*2,f'guard/{blocked}')
for direction,active,flags,clear,normal in itertools.product([0,1,6],[0,1],[0,2,0xffff],[0,1],[(0,0,-1),(0,0,1),(0,0,0)]):
 g=LedgeGraph();g.contact(direction,active,flags,clear,normal);g.run([call(0x52bc70,P,[Q])],f'contact gates/{direction}/{active}/{flags}/{clear}/{normal}')
for top,moving,direction in itertools.product([-10,0,3,8,12,17.9,18,20,32],[False,True],[0,1,6]):
 g=LedgeGraph();g.contact(direction);g.obstacle(top=top,moving=moving);g.run([call(0x52bc70,P,[Q])]*2,f'ledge height/{top}/{moving}/{direction}')
for selected,stale in itertools.product([1,2,3,4,5,6,7],[False,True]):
 g=LedgeGraph();g.obstacle(top=9)
 for i,direction in enumerate([0,1,6]):g.contact(direction,int(bool(selected&(1<<i))),2 if stale and i==2 else 0,int(stale))
 g.run([call(0x52bc70,P,[Q])],f'multiple candidates/{selected}/{stale}')
for mask,moving,live in itertools.product([0,1,0x55,0xfe],[False,True],[False,True]):
 g=LedgeGraph();g.contact(0);g.obstacle(top=12,moving=moving);g.put(PLATFORM+0xac,'<4f',1,2,3,1)
 if not live:g.put(GATE+0x18,'<I',0)
 g.run([call(0x52bc70,P,[Q])],f'cache registry/platform/{mask}/{moving}/{live}',{0x69190c:mask})
for high,low,gravity,offset in itertools.product([6,18,30],[0,2],[0,450,900],[0,2]):
 g=LedgeGraph();g.parameters(overrides={0xa5e2da58:gravity,0xac96d24b:.175,0xda85f5ae:high,0x6da7f696:low,0x78e6a5ec:45,0x72660978:offset});g.contact(0);g.obstacle(top=high*.5)
 g.run([call(0x52bc70,P,[Q])],f'jump parameters/{high}/{low}/{gravity}/{offset}')
callback_records=[]
for mutation,moving in itertools.product(['observe','cancel','face','position','owner','velocity','trigger owner'],[False,True]):
 g=LedgeGraph();g.contact(0);g.obstacle(top=12,moving=moving);g.trigger(mutation)
 stages=g.run([call(0x52bc70,P,[Q])],f'real trigger callback/{mutation}/{moving}')
 assert oracle.word(CBSTATE)==1,(mutation,moving)
 assert stages[0]['result']==1
 assert oracle.word(P+0x18)==(0 if mutation=='cancel' else 1)
 callback_records.append({'mutation':mutation,'moving':moving,'result':1,'state':oracle.word(P+0x18),'callbacks':oracle.word(CBSTATE)})
# Full contact collection and velocity response, including repeated retained refs.
for movement_state,shape,velocity,dt in itertools.product([0,1,2],['empty','wall','moving wall','near wall','behind'],[(0,0,3,1),(2,0,3,1),(0,0,-3,1),(0,0,0,1)],[0,.125]):
 g=LedgeGraph();g.put(P+0x18,'<I',movement_state);g.put(P+0x34,'<4f',*velocity);g.put(P+0x80,'<f',dt);g.put(P+0x44,'<f',4);g.put(P+0x1798,'<f',1);g.put(P+0x704,'<f',20)
 if shape!='empty':g.obstacle(top=32,z=.1 if shape=='near wall' else -2 if shape=='behind' else 2,moving=shape=='moving wall')
 g.run([call(0x52c2c0,P,[Q])]*2,f'full contacts/{movement_state}/{shape}/{velocity}/{dt}')
for normal in [(0,0,0,1),(1,0,0,1),(1,.499,2,1),(1,.5,2,1),(1,1,2,1)]:
 g=LedgeGraph();g.put(P+0x1794,'<4f',*normal);g.run([call(0x52c2c0,P,[Q])],f'slope separation/{normal}')
# Opposing/orthogonal walls and moving surfaces exercise the constraint graph.
for geometry,velocity,moving in itertools.product(['corner','corridor'],[(0,0,0,1),(1,0,1,1),(10,0,3,1)],[False,True]):
 g=LedgeGraph();g.put(P+0x1798,'<f',1);g.put(P+0x34,'<4f',*velocity);g.put(P+0x704,'<f',20)
 for axis,sign in ([('z',1),('x',1)] if geometry=='corner' else [('z',1),('z',-1)]):
  actor,owner=g.obstacle(top=32,z=2*sign,moving=moving);geo=g.word(actor+12);verts=g.word(geo+48)
  if sign<0:g.put(g.word(geo+12)+6,'<2H',1,2)
  if axis=='x':
   g.put(verts,'<9f',2,-32,-32,2,-32,32,2,32,0);g.put(geo+16,'<8f',2,-32,-32,1,2,32,32,1);g.put(g.word(geo+12)+6,'<2H',1,2)
  if moving:g.put(owner+0xac,'<4f',-5 if axis=='x' else 0,0,-5*sign if axis=='z' else 0,1)
 g.run([call(0x52c2c0,P,[Q])],f'multiple constraints/{geometry}/{velocity}/{moving}')
for velocity,surface in itertools.product([(1,0,100,1),(1e-6,0,2e-6,1),(10,0,3,1),(3,0,1,1)],[-5,0,5]):
 g=LedgeGraph();g.put(P+0x34,'<4f',*velocity);g.put(P+0x1798,'<f',1);g.put(P+0x704,'<f',20)
 _,owner=g.obstacle(top=32,z=2,moving=True);g.put(owner+0xac,'<4f',0,0,surface,1)
 g.run([call(0x52c2c0,P,[Q])],f'projection limits/{velocity}/{surface}')
for up,vertical in [(True,-10),(False,100)]:
 g=LedgeGraph();g.put(P+0x18,'<I',1);g.put(P+0x80,'<f',.125);g.put(P+0x44,'<f',vertical);g.put(P+0x34,'<4f',0,0,0,1)
 g.plane(-.5 if up else .5,moving=False,up=up);g.run([call(0x52c2c0,P,[Q])],f'airborne floor classification/{up}')
for gate in ['dead contact','same platform','latched timer','new timer','wrapped timer','cancelled control']:
 g=LedgeGraph();g.put(P+0x1798,'<f',1);actor,owner=g.obstacle(top=32,z=2,moving=True)
 if gate=='dead contact':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 if gate=='same platform':g.put(CONTACT,'<I',owner);g.put(PLATFORM+4,'<I',0);g.put(owner+4,'<I',CONTACT)
 if 'timer' in gate:
  g.put(P+0x98,'<B',1);g.put(P+0x17a8,'<B',0 if gate=='new timer' else 1);g.put(P+0x17ac,'<I',0xffffffff if gate=='wrapped timer' else 0)
 if gate=='cancelled control':g.put(CONTROL+0x26,'<B',1)
 g.run([call(0x52c2c0,P,[Q])],f'contact gates/{gate}',{0x7d1ec8:0x80000000 if gate=='wrapped timer' else 100})
rng=random.Random(0x52c2c0)
for trial in range(80):
 g=LedgeGraph();theta=rng.uniform(-3,3);nx,nz=math.sin(theta),math.cos(theta);distance=rng.uniform(.05,3.9);moving=bool(trial%2)
 actor,owner=g.obstacle(top=32,z=2,moving=moving);geo=g.word(actor+12);verts=g.word(geo+48);cx,cz=-nx*distance,-nz*distance;tx,tz=-nz,nx
 points=[(cx-32*tx,-32,cz-32*tz),(cx+32*tx,-32,cz+32*tz),(cx,32,cz)]
 g.put(verts,'<9f',*(value for point in points for value in point));g.put(geo+16,'<8f',min(t[0] for t in points),-32,min(t[2] for t in points),1,max(t[0] for t in points),32,max(t[2] for t in points),1)
 g.put(P+0x34,'<4f',rng.uniform(-20,20),rng.uniform(-2,2),rng.uniform(-20,20),1);g.put(P+0x48,'<4f',math.sin(theta+.5),0,math.cos(theta+.5),1);g.put(P+0x1798,'<f',1);g.put(P+0x704,'<f',rng.choice([0,3,4,5,20]))
 if moving:g.put(owner+0xac,'<4f',rng.uniform(-10,10),0,rng.uniform(-10,10),1)
 g.run([call(0x52c2c0,P,[Q])],f'finite oblique contact/{trial}')
parent_records=[]
for route,mutation in itertools.product(['ledge','rail auto','rail forced'],['observe','cancel']):
 g=LedgeGraph();g.put(P+0x1798,'<f',1);g.put(P+0x98,'<B',1);g.put(P+0x17a8,'<B',1);g.put(P+0x17ac,'<I',0)
 if route=='ledge':g.obstacle(top=12,z=2);g.trigger(mutation)
 else:
  g.rail_nodes(2);g.put(P+0x24,'<4f',0,0,20,1);g.obstacle(top=32,z=22)
  if route=='rail forced':g.put(P+0x98,'<B',0);g.put(INPUT+0x100,'<B',1)
 stages=g.run([call(0x52c2c0,P,[Q])],f'contact transition/{route}/{mutation}',{0x7d1ec8:1000})
 assert stages[0]['result']==0 and oracle.word(P+0x18)==(4 if route!='ledge' else 0 if mutation=='cancel' else 1),(route,mutation,stages[0]['result'],oracle.word(P+0x18))
 parent_records.append({'route':route,'mutation':mutation,'return':stages[0]['result'],'state':oracle.word(P+0x18),'callbacks':oracle.word(CBSTATE)})
# Real ground parent through collision, facing response and position movement.
# Stop before the unavailable floor handler; never invent its gameplay return.
ground_hits=Counter();ground_active=False
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:ground_hits.update([at]),begin=0x52d300,end=0x52d4ae)
def ground_boundary(cpu,at,size,user):
 if ground_active:cpu.mem_write(BOUNDARY,struct.pack('<4I',at,0,P,1));cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,ground_boundary,begin=0x52b370,end=0x52b370)
prefix_records=[]
for scenario,amount in itertools.product(['empty','wall','moving wall','ledge','cancelled'],[0,.4,1]):
 g=LedgeGraph();g.put(P+0x1798,'<f',1);g.put(OBJ+0x4c,'<4f',0,0,0,1);g.put(P+0x94,'<f',amount);g.put(P+0x704,'<f',20)
 if scenario!='empty':g.obstacle(top=12 if scenario=='ledge' else 32,z=2,moving=scenario=='moving wall')
 if scenario=='ledge':g.put(P+0x98,'<B',1);g.put(P+0x17a8,'<B',1);g.put(P+0x17ac,'<I',0)
 if scenario=='cancelled':g.put(CONTROL+0x26,'<B',1)
 stages=g.run([],f'ground contact prefix/{scenario}/{amount}',{0x7d1ec8:1000});cpu=oracle.cpu;before=bytes(cpu.mem_read(BASE,len(initial)));sp=oracle.stack+0x18000
 cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,P);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 ground_active=True
 try:cpu.emu_start(0x52d300,oracle.stop,count=12000000)
 finally:ground_active=False
 trap=cpu.reg_read(UC_X86_REG_EIP)==0x52b370
 assert trap or cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
 if trap:assert oracle.word(BOUNDARY)==0x52b370
 else:assert oracle.word(P+0x18)!=0 or cpu.mem_read(CONTROL+0x26,1)!=b'\0'
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 assert len(root_records)==len(stack_records)==1
 stages.append({'fn':'0x52d300','this':P,'args':[Q,DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':trap,'boundary_factory':0x52b370,'stack_objects':stack_records[0],**root_records[0],'indeterminate_words':sorted(undefined_words),'indeterminate_provenance':[undefined_provenance[a] for a in sorted(undefined_words)]})
 oracle.counts['thug_walk_ground_contacts_prefix_draft']+=1;prefix_records.append({'scenario':scenario,'amount':amount,'interrupted':trap,'state':oracle.word(P+0x18)})
scope='Two complete original routines recover ledge jumps and full eight-probe Walk contact handling, including moving-surface velocity, timed/forced rail gates, script cancellation, separation and ordered velocity constraints. The ground parent now executes these handlers and position movement before stopping explicitly at52b370; genuine state/control exits return normally, but the parent is not counted complete. All defined arena/global values compare. Copied probe unknown_a8 and conditionally unset scene words receive four-byte definedness allowances only when source-write tracing proves them uninitialized, ending on any later write; retained probe/cache pointers are checked for Wasm stack identity and lifetime. No numeric masks, NaN classification or quieting. Initialized graphs, finite inputs and valid cache/rail capacities are contracts. Full ground/Walk frames, remaining startup/rendering and original playable training remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x52b370,'indeterminate_word_addresses':[P+0xbc+i*0xcc+offset for i in range(8) for offset in [0x70,0xa8]],'stack_probe_pointer_fields':[P+0xbc+i*0xcc+0x64 for i in range(8)],'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'native_callbacks':[*extra.get('native_callbacks',[]),{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-ledge',scope,{},extra);coverage.update(saved)
p=folder/'walk-ledge-original.json';report=json.loads(p.read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()};report['callback_records']=callback_records;report['parent_records']=parent_records;report['ground_prefix_records']=prefix_records;report['ground_prefix_coverage']={'covered':len(ground_hits),'total':134,'addresses':[hex(a) for a in sorted(ground_hits)]}
p.write_text(json.dumps(report,indent=2)+'\n');(folder/'walk-ledge-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');print(json.dumps(report['instruction_coverage']))
