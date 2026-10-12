"""Original floor-transition prerequisites with real rails, collision and QB callbacks."""
from pathlib import Path
source=Path('local/analysis/probe-walk-transition.py').read_text().split('for flag_index,enabled,gravity')[0]
exec(compile(source,'<preserved Walk transition graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x441190,194,'thug_walk_enter_rail_top_draft',0,'void',False,False,True),
 (0x441fc0,420,'thug_walk_try_rail_top_draft',0,'byte',True,False,True),
 (0x43dc00,91,'thug_walk_ledge_blend_height_draft',0,'double',False,False,True),
 (0x43dc60,136,'thug_walk_hang_height_draft',0,'double',False,False,True),
 (0x43dcf0,214,'thug_walk_enter_hang_draft',0,'void',True,True,True),
 (0x57cb20,62,'thug_rail_transform_vector_draft',2,'word',False,False,True),
 (0x57c540,85,'thug_ledge_target_copy_draft',1,'void',False,False,True),
 (0x5299f0,750,'thug_walk_try_grind_draft',0,'byte',False,True,True),
 (0x43ddd0,490,'thug_walk_hang_vertical_clear_draft',3,'byte',False,False,True),
 (0x57c5a0,81,'thug_rail_nodes_coincident_draft',2,'byte',False,False,True),
 (0x57e170,341,'thug_rail_find_coincident_draft',3,'byte',False,False,True),
 (0x43e230,753,'thug_walk_follow_ledge_draft',5,'byte',False,True,True)]
for row in specs:bind_new(*row)
bind(0x417760,'thug_collision_probe_initialize',0,'word',False,False)
function_exports.append([0x441190,'thug_walk_enter_rail_top_draft']);fields.add(P+0x1948)
source=Path('local/analysis/probe-trigger.py').read_text();exec(compile(source[source.index('RECORDS,EVENTS,CBSTATE'):source.index('for flags in [0,1,2,3')],'<preserved QB observer>','exec'))
TRIGGER,CONTROL,MODEL,ANIM,HANG,ORIENT=P+0xd000,P+0xd100,P+0x11000,P+0x11400,P+0x11500,P+0x11600
if 0x7ce5d8 not in index:glob('thug_skater_orientation_context',0x7ce5d8,ORIENT)
else:defaults[index[0x7ce5d8]]=ORIENT
if not any(x[0]==0x64637c for x in exports):exports.append([0x64637c,'thug_attachment_provider_methods'])
# Terminal diagnostic boundary preserves the original format, integer and double arguments.
def floor_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0]
 count=oracle.word(DLOG);assert count<32;oracle.setword(DLOG,count+1);row=bytearray(128);row[:len(fmt)]=fmt
 if fmt==b'Tracking%d %.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n':
  row[64:68]=cpu.mem_read(sp+8,4);row[72:120]=cpu.mem_read(sp+12,48)
 else:
  assert fmt==b'M:%s:%i: %s\n',fmt
  file=bytes(cpu.mem_read(oracle.word(sp+8),32)).split(b'\0')[0];message=bytes(cpu.mem_read(oracle.word(sp+16),28)).split(b'\0')[0]
  assert file==b'omponents\\WalkHangUtil.cpp' and message in [b'BAD ANGLE ON COINCIDENT RAIL',b'FOUND COINCIDENT RAIL']
  row[64:64+len(file)]=file;row[96:96+len(message)]=message;row[124:128]=cpu.mem_read(sp+12,4)
 cpu.mem_write(DLOG+16+128*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=floor_debug.__code__
initial=bytes(memory);oracle.initial=initial
class FloorGraph(TransitionGraph):
 cached=TriggerGraph.cached
 level_nodes=TriggerGraph.level_nodes
 callback=TriggerGraph.callback
 def rail_nodes(self,count=1,entering=True,changed=False):
  nodes=super().rail_nodes(count,entering,changed)
  for node in nodes:self.put(self.word(node+0x40)+0x40,'<2I',0,node)
  return nodes
 def __init__(self):
  super().__init__();self.image[TRIGGER-BASE:CONTROL-BASE+0x100]=bytes(0x200);self.image[MODEL-BASE:MODEL-BASE+0x800]=bytes(0x800)
  self.image[PHYSICS-BASE:PHYSICS-BASE+0x1550]=bytes(0x1550);self.image[STATE-BASE:STATE-BASE+0x128]=bytes(0x128)
  self.put(P+0x1778,'<I',MODEL);self.put(MODEL+0x208,'<I',ANIM);self.put(P+0x1780,'<I',CONTROL)
  self.put(P+0x177c,'<I',TRIGGER);self.put(TRIGGER,'<6I',0x646648,0xe594f0a2,0,OBJ,0,0);fields.add(TRIGGER)
  self.put(HANG,'<6I',0x647618,0x380d909a,0,OBJ,0,0);fields.add(HANG);self.put(OBJ+0x100,'<I',HANG);self.put(ORIENT+0x40,'<I',0xd443a2bc)
  self.put(PHYSICS+12,'<I',OBJ);self.put(PHYSICS+0x1510,'<I',TRIGGER);self.put(PHYSICS+0x1528,'<I',STATE);self.put(PHYSICS+0x152c,'<I',GATE)
  self.put(STATE+12,'<I',OBJ);self.put(STATE+0x18,'<I',1);self.put(GATE+12,'<I',OBJ)
  self.put(P+0x68,'<4f',-20,0,0,1);self.put(P+0x24,'<4f',20,0,0,1);self.put(P+0x48,'<4f',0,0,1,1)
  self.parameters(overrides={0xac96d24b:.175,0xc4c164e8:200,0xa2735dd9:50,0x76bf49e0:12,0x35b3bbda:6,0xa8c13e74:60,0xde86132e:30,0x7201ad48:.5,0xc3263e6e:8})
  self.symbol(0xf840753e,2,bits(12));self.symbol(0x19fb78fa,1,0);self.registry([(0x1cdfb2a3,0)]);self.rail_nodes(0)
  self.image[RECORDS-BASE:ALTOWNER-BASE+0x324]=bytes(ALTOWNER-RECORDS+0x324)
  self.put(ALTOWNER,'<I',0x647650);fields.add(ALTOWNER);self.put(ALTOWNER+0x4c,'<4f',7,8,9,1);self.put(ALTOWNER+0x100,'<I',HANG);self.cached(5)
 def grind_nodes(self,kind='segment',rail=RAIL,height=0):
  array=self.alloc(3*0x54);self.put(rail,'<16f',*IDENTITY);self.put(rail+0x40,'<3I',array,0,3)
  for i in range(3):
   at=array+i*0x54;self.put(at,'<12f',0,height,-30+30*i,1,0,height,30*i,1,0,height,-30+30*i,1)
   self.put(at+0x40,'<5I',array+(i+1)*0x54 if kind=='segment' and i<2 else 0,array+(i-1)*0x54 if kind=='segment' and i else 0,4,0x110+i,0)
  return array
 def moving_grind(self,miss_first=False,angle=0,scale=1):
  import math
  component=self.alloc(28);transform=self.alloc(0x54);owner=self.alloc(0x110)
  self.put(component,'<7I',0x64637c,0x1cdfb2a3,0,owner,0,0,transform);fields.add(component)
  c,s=math.cos(angle)*scale,math.sin(angle)*scale;self.put(owner+0x6c,'<16f',c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1);self.put(owner+0x4c,'<4f',100,20,-50,1)
  nodes=self.grind_nodes(rail=transform)
  self.put(P+0x68,'<4f',100-20*c,20,-50+20*s,0);self.put(P+0x24,'<4f',100+20*c,20,-50-20*s,-2)
  head=component
  if miss_first:
   head=self.alloc(28);empty=self.alloc(0x54);self.put(head,'<7I',0x64637c,0x1cdfb2a3,0,owner,0,component,empty);fields.add(head);self.put(empty,'<16f',*IDENTITY)
  return head,component,transform,nodes

for flags,progress,height in itertools.product([0,1,8,255],[-2,-0.0,.2,1,2],[0,.5,60]):
 g=FloorGraph();g.put(ANIM+0x44,'<B',flags);g.put(ANIM+0x20,'<f',progress);g.parameters(overrides={0xa8c13e74:height})
 g.run([call(0x43dc00,P)]*2,f'animation blend/{flags}/{progress}/{height}')
for high,scale,model in itertools.product([-30,0,30,100],[0,.125,.5,1,2],[-20,0,60]):
 g=FloorGraph();g.parameters(overrides={0xde86132e:high,0x7201ad48:scale,0xa8c13e74:model});g.run([call(0x43dc60,P)]*2,f'hang height/{high}/{scale}/{model}')
for changed,source_offset,output_offset in itertools.product([0,1],[0,0x20,0x30,0x100],[-4,0,4,8,64]):
 g=FloorGraph();g.put(RAIL,'<16f',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16);g.put(RAIL+source_offset,'<4f',2,3,4,5);g.put(RAIL+0x50,'<B',changed)
 g.run([call(0x57cb20,RAIL,[RAIL+source_offset+output_offset,RAIL+source_offset])],f'rail vector alias/{changed}/{source_offset}/{output_offset}')
for alignment,offset in itertools.product([0,1,4],[-52,-4,0,4,20,48,52]):
 g=FloorGraph();at=P+0xf000+alignment;g.put(at,'<13I',*[0x11223344+i*0x10101 for i in range(13)])
 g.run([call(0x57c540,at+offset,[at])],f'target forward copy/{alignment}/{offset}')
for changed,backward,endpoint in itertools.product([False,True],[False,True],[(0,100,0,1),(1,1,1,1),(0,0,0,1),(1e-10,2e-10,3e-10,1)]):
 g=FloorGraph();g.put(NODE+0x20,'<4f',0,0,0,1);g.put(NEXT+0x20,'<4f',*endpoint);g.put(NODE+0x40,'<2I',0 if backward else NEXT,NEXT if backward else 0)
 g.put(RAIL,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,7,8,9,1);g.put(RAIL+0x50,'<B',changed);g.put(P+0x1764,'<I',NODE);g.put(P+0x176c,'<I',RAIL)
 g.run([call(0x441190,P)]*2,f'upper rail callback/{changed}/{backward}/{endpoint}')
rail_records=[]
for blocked,count,shape in itertools.product([0,1],[0,1,3],['valid','reversed','far','flag','slope']):
 g=FloorGraph();nodes=g.rail_nodes(count,entering=False);g.put(STATE+0x70,'<B',blocked);g.put(P+0x24,'<4f',0,100,0,1)
 for node in nodes:
  if shape=='reversed':g.put(g.word(node+0x40)+0x24,'<f',200)
  if shape=='far':g.put(node+0x20,'<f',1000)
  if shape=='flag':g.put(node+0x48,'<I',4)
  if shape=='slope':g.put(g.word(node+0x40)+0x20,'<f',50)
 calls=[call(0x441fc0,P,[Q])]
 success=not blocked and count>0 and shape=='valid'
 if success:calls.append(call(0x441190,P))
 stages=g.run(calls,f'upper rail search/callback/{blocked}/{count}/{shape}')
 assert stages[0]['result']==int(success)
 if success:assert oracle.word(P+0x18)==3;rail_records.append({'count':count,'selected':oracle.word(P+0x1764),'state':3})
# Actual callback can mutate the owner and live component state.
callback_records=[]
for mode,node_present,rail_present in itertools.product(['empty','script','mutating'],[False,True],[False,True]):
 g=FloorGraph();node=g.grind_nodes();g.put(P+0x1764,'<I',node if node_present else 0);g.put(P+0x176c,'<I',RAIL if rail_present else 0)
 g.put(HANG+0x1d,'<B',1);g.put(P+0x18,'<I',1)
 if node_present and mode!='empty':
  g.level_nodes([(0x110,[(0x2ca8a299,13,6)])]);g.callback([(P+12,ALTOWNER),(HANG+0x1d,7)] if mode=='mutating' else [])
 stages=g.run([call(0x43dcf0,P)],f'hang callback/{mode}/{node_present}/{rail_present}')
 assert oracle.word(P+0x18)==2 and oracle.cpu.mem_read(HANG+0x1d,1)==b'\0'
 callback_records.append({'mode':mode,'node':node_present,'rail':rail_present,'callbacks':oracle.word(CBSTATE)})
# Real fixed and moving rail search, eligibility and segment clearance.
grind_records=[]
for kind,blocked,reject,diagnostic in itertools.product(['empty','point','segment','moving','second moving'],[False,True],[False,True],[False,True]):
 g=FloorGraph();changes={};nodes=0
 if kind in ['point','segment']:nodes=g.grind_nodes(kind)
 if 'moving' in kind:
  head,component,transform,nodes=g.moving_grind(kind=='second moving');changes[0x6f0db8]=head
 if reject:
  g.put(PHYSICS+0x22c,'<I',nodes);g.put(STATE+0xa8,'<B',1);g.put(STATE+0xd0,'<B',1)
 g.put(CONTROL+0x24,'<B',blocked);g.symbol(0x19fb78fa,1,int(diagnostic))
 stages=g.run([call(0x5299f0,P,[Q])],f'grind/{kind}/{blocked}/{reject}/{diagnostic}',changes)
 grind_records.append({'kind':kind,'blocked':blocked,'reject':reject,'diagnostic':diagnostic,'result':stages[0]['result'],'tracking_calls':oracle.word(DLOG)})
for angle,scale in itertools.product([.3,-.7,1.1],[.5,1,2]):
 g=FloorGraph();head,*_=g.moving_grind(angle=angle,scale=scale);g.run([call(0x5299f0,P,[Q])],f'transformed moving grind/{angle}/{scale}',{0x6f0db8:head})
collision_records=[]
for moving,height in itertools.product([False,True],[-7,-6,-5,0,5,6,7]):
 g=FloorGraph();g.grind_nodes('point',height=-10);g.put(P+0x68,'<4f',0,0,0,1);g.put(P+0x24,'<4f',0,0,0,1);g.plane(height-10,moving=moving)
 stages=g.run([call(0x5299f0,P,[Q])]*2,f'grind collision distance/{moving}/{height}')
 collision_records.append({'moving':moving,'height':height,'result':stages[0]['result']})
# Hanging clearance retains the caller's probe, including moving references.
vertical_records=[]
for moving,up,height,normal in itertools.product([False,True],[False,True],[-80,-30,0,15,40],[(0,0,1,1),(1,.2,-.3,1)]):
 g=FloorGraph();probe=P+0x12000;target=probe+0x100;side=target+0x40
 g.parameters(overrides={0xafbf7687:2,0xc3263e6e:8,0xa8c13e74:60,0xde86132e:30,0x7201ad48:.5,0x8f35f29f:12})
 g.put(target,'<13f',0,0,0,1,*normal,0,0,0,0,0);g.put(side,'<4f',1,0,0,1);g.plane(height,moving=moving,up=up)
 stages=g.run([call(0x417760,probe)]+[call(0x43ddd0,P,[probe,target,side,Q])]*2,f'vertical hang clearance/{moving}/{up}/{height}/{normal}')
 vertical_records.append({'moving':moving,'up':up,'height':height,'result':stages[1]['result']})
rng=random.Random(0x43ddd0)
for trial in range(20):
 g=FloorGraph();probe=P+0x12000;target=probe+0x100;side=target+0x40
 g.parameters(overrides={0xafbf7687:.3,0xc3263e6e:.7,0xa8c13e74:6.2,0xde86132e:3.5,0x7201ad48:.2,0x8f35f29f:1.2})
 g.put(target,'<13f',*[rng.uniform(-10,10) for _ in range(13)]);g.put(side,'<4f',*[rng.uniform(-3,3) for _ in range(4)])
 g.run([call(0x417760,probe),call(0x43ddd0,P,[probe,target,side,Q])],f'vertical hang finite arithmetic/{trial}')
for axis,delta in itertools.product(range(3),[-2,-1.0001,-1,-.9999,-0.0,.9999,1,1.0001,2]):
 g=FloorGraph();g.put(NODE+0x20,'<4f',0,0,0,1);values=[0,0,0,1];values[axis]=delta;g.put(NEXT+0x20,'<4f',*values)
 stages=g.run([call(0x57c5a0,RAIL,[NODE,NEXT])],f'rail coincidence threshold/{axis}/{delta}');assert stages[0]['result']==int(abs(delta)<=1)

def ledge_nodes(g,positions,links,flags=None):
 nodes=g.alloc(len(positions)*0x54);g.put(RAIL+0x40,'<3I',nodes,0,len(positions))
 for i,position in enumerate(positions):
  at=nodes+i*0x54;g.image[at-BASE:at-BASE+0x54]=bytes(0x54);g.put(at+0x20,'<4f',*position,1)
  next_,previous=links[i];g.put(at+0x40,'<3I',nodes+next_*0x54 if next_ is not None else 0,nodes+previous*0x54 if previous is not None else 0,4 if flags is None else flags[i])
 return [nodes+i*0x54 for i in range(len(positions))]
coincident_records=[]
for shape,mask,changed,obstacle in itertools.product(['outgoing','incoming','both','neither','self','far x','far y','far z','flag missing','flag filtered','previous flag missing','previous flag filtered'],[0,0x28],[False,True],[False,True]):
 g=FloorGraph();positions=[(0,0,0),(10,0,0),(-10,0,0)];links=[(1,2),(None,0),(0,None)];flags=[4,4,4]
 if shape=='incoming':links[0]=(None,2)
 if shape=='outgoing':links[0]=(1,None)
 if shape=='neither':links[0]=(None,None)
 if shape.startswith('far '):positions[0]=tuple(2 if i=={'far x':0,'far y':1,'far z':2}[shape] else 0 for i in range(3))
 if shape in ['flag missing','flag filtered']:flags[0]=0 if shape=='flag missing' else 0x24;links[0]=(1,None)
 if shape.startswith('previous flag'):flags[2]=0 if shape=='previous flag missing' else 0x24;links[0]=(None,2)
 nodes=ledge_nodes(g,positions,links,flags);g.put(NODE+0x20,'<4f',0,0,0,1);g.put(RAIL+0x50,'<B',changed)
 if obstacle:g.put(ORIENT+0x40,'<I',0);g.wall(z=0)
 stages=g.run([call(0x57e170,RAIL,[nodes[0] if shape=='self' else NODE,mask,P+0x12000,Q])],f'find coincident rail/{shape}/{mask}/{changed}/{obstacle}')
 coincident_records.append({'shape':shape,'mask':mask,'changed':changed,'obstacle':obstacle,'result':stages[0]['result']})
for count in [0,-1]:
 g=FloorGraph();g.put(RAIL+0x48,'<i',count);g.put(NODE+0x20,'<4f',0,0,0,1)
 stages=g.run([call(0x57e170,RAIL,[NODE,0x28,P+0x12000,Q])],f'empty coincident rail array/{count}');assert stages[0]['result']==0
# Direct neighbor selection plus disconnected, reversed and acute-angle joins.
follow_records=[]
import math
for direction,shape,angle,obstacle in itertools.product([-0.5,1.5],['direct','duplicate','reversed','absent','flag missing','flag blocked'],[0,2.6,2.7],[False,True]):
 g=FloorGraph();positive=direction>0;join=10 if positive else 0;dx,dz=10*math.cos(angle),10*math.sin(angle)
 positions=[(0,0,0),(10,0,0),(join,0,0),(join+(dx if positive else -dx),0,dz)]
 links=[(1,None),(None,0),(3,None),(None,2)];flags=[4]*4
 if shape=='direct':
  if positive:links[1]=(3,0)
  else:links[0]=(1,3);links[3]=(0,None)
  positions[2]=(100,0,0)
 if shape=='reversed':positions[2],positions[3]=positions[3],positions[2]
 if shape=='absent':positions[2]=(100,0,0);positions[3]=(110,0,0)
 if shape=='flag missing':flags[2]=0
 if shape=='flag blocked':flags[2]=0x2c
 nodes=ledge_nodes(g,positions,links,flags);g.put(P+0x176c,'<I',RAIL);g.put(P+0x12000,'<f',direction)
 if obstacle:g.put(ORIENT+0x40,'<I',0);g.wall(z=0)
 stages=g.run([call(0x43e230,P,[P+0x12000,nodes[0],nodes[1],P+0x12004,P+0x12008,Q])],f'follow ledge/{direction}/{shape}/{angle}/{obstacle}')
 follow_records.append({'direction':direction,'shape':shape,'angle':angle,'obstacle':obstacle,'result':stages[0]['result'],'diagnostics':oracle.word(DLOG)})

scope='Twelve complete floor-transition prerequisites recover upper-side rail selection/callback, ledge blend and hanging heights, hanging entry with actual QB events, rail-space vector/target copies fixed/moving grind selection with final collision clearance, two-direction hanging clearance and connected/coincident ledge continuation. Entire arena/globals and completed-call preserved registers compare. Explicit selection-to-callback calls do not recover the intervening animation frame. Full ledge selection, floor handling, ground/Walk frames, startup and browser playability remain unfinished.'
extra={**extra,'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-floor',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-floor-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()};report['rail_records']=rail_records;report['callback_records']=callback_records;report['grind_records']=grind_records;report['collision_records']=collision_records;report['vertical_records']=vertical_records;report['coincident_records']=coincident_records;report['follow_records']=follow_records
(folder/'walk-floor-original.json').write_text(json.dumps(report,indent=2)+'\n');(folder/'walk-floor-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');print(json.dumps(report['instruction_coverage']))
