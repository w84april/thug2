"""Original Walk state transitions, vertical-rail selection and entry helpers."""
from pathlib import Path
source=Path('local/analysis/probe-walk-ground.py').read_text().split("for kind in ['absent'")[0]
exec(compile(source,'<preserved ground graph setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x5284c0,149,'thug_walk_gravity_draft',0,'double',False,False,False),
 (0x5260e0,384,'thug_walk_change_state_draft',1,'void',False,False,True),
 (0x52ab90,376,'thug_walk_leave_platform_draft',2,'void',True,False,True),
 (0x527720,139,'thug_walk_prepare_facing_draft',2,'void',False,False,True),
 (0x528220,84,'thug_walk_probe_direction_draft',2,'word',False,False,True),
 (0x57cfb0,212,'thug_rail_orientation_draft',2,'word',False,False,True),
 (0x4410c0,200,'thug_walk_enter_rail_draft',0,'void',False,False,True),
 (0x441260,369,'thug_walk_rail_exit_target_draft',4,'byte',False,False,False),
 (0x4418b0,706,'thug_walk_rail_entry_target_draft',4,'byte',False,False,True),
 (0x57d880,407,'thug_walk_find_rail_draft',7,'byte',False,False,True),
 (0x441de0,479,'thug_walk_try_rail_draft',1,'byte',True,False,True)]
for row in specs:bind_new(*row)
functions[hex(0x57d880)]['float_args']=[1,2]
functions[hex(0x441260)]['cleanup']=16
function_exports.append([0x4410c0,'thug_walk_enter_rail_draft']);fields.add(P+0x1948)
if 0x7ce4fd not in index:glob('thug_last_gameplay_flag',0x7ce4fd,0,1)
initial=bytes(memory);oracle.initial=initial
FLAGS=P+0x8000
RAIL,NODE,NEXT,PHYSICS,STATE=P+0x9000,P+0x9100,P+0x9200,P+0xa000,P+0xc000
class TransitionGraph(GroundGraph):
 def __init__(self):
  super().__init__();self.put(GAME+0x20,'<I',FLAGS);self.image[FLAGS-BASE:FLAGS-BASE+0x800]=bytes(0x800)
  self.parameters(overrides={0xa5e2da58:900,0xac96d24b:.175,0x5296e3fd:40,0x76bf49e0:12,0x35b3bbda:6,0x456f216d:45,0x0eecd255:100,0xa2735dd9:50,0xc4c164e8:200});self.symbol(0x9c8c6df1,1,3)
  self.put(P+0x80,'<f',.125)
  self.put(GAME+0x24,'<I',RAIL);self.put(RAIL,'<16f',*IDENTITY);self.put(P+0x178c,'<I',PHYSICS);self.put(PHYSICS+0x1528,'<I',STATE);self.put(STATE+0x70,'<B',0)
 def rail_nodes(self,count=1,entering=True,changed=False):
  array=self.alloc(max(1,count)*0x54);self.nodes=[]
  self.put(RAIL+0x40,'<3I',array,0,count);self.put(RAIL+0x50,'<B',int(changed))
  for i in range(count):
   at=array+i*0x54;end=self.alloc(0x54);self.nodes.append(at)
   self.put(at+0x20,'<4f',i*2,0 if entering else 100,0,1);self.put(end+0x20,'<4f',i*2,100 if entering else 0,0,1)
   self.put(at+0x30,'<4f',0,0,0,1);self.put(end+0x30,'<4f',0,0,0,1);self.put(at+0x40,'<4I',end,0,0x24,0x12340000+i)
  return self.nodes
for flag_index,enabled,gravity in itertools.product([0,3,31,32,63,127,0xffffffff],[0,1],[-100,0,900,1e-30,1e30]):
 g=TransitionGraph();g.symbol(0x9c8c6df1,1,flag_index);signed=flag_index if flag_index<0x80000000 else flag_index-0x100000000
 g.put(FLAGS+0x5f0+(signed>>5)*4,'<I',(1<<(flag_index&31)) if enabled else 0);g.parameters(overrides={0xa5e2da58:gravity,0xac96d24b:.175})
 g.run([call(0x5284c0)]*2,f'gravity gameplay flag/{flag_index}/{enabled}/{gravity}',{0x7ce4fd:0xa5})
for previous,state,fill in itertools.product([0,1,2,3,4,5,0xffffffff],[0,1,2,3,4,5,0xffffffff],[0,0xa5]):
 g=TransitionGraph();g.image[P-BASE:P-BASE+0x1960]=bytes([fill])*0x1960;g.put(P+0x1770,'<I',INPUT);g.put(P+0x18,'<I',previous)
 g.run([call(0x5260e0,P,[state])]*2,f'change state/{previous}/{state}/{fill}')
for seconds,counter,offset in itertools.product([-.125,0,.001,.175,2],[0,1,10000,0x7fffffff,0xffffffff],[0,0xffffffff]):
 g=TransitionGraph();g.parameters(overrides={0xa5e2da58:900,0xac96d24b:seconds});g.put(P+0x18,'<I',1)
 g.run([call(0x5260e0,P,[2]),call(0x5260e0,P,[1]),call(0x5260e0,P,[0])],f'buffered input/timing/{seconds}/{counter}/{offset}',{0x7d1ec8:counter,0x696d60:offset})
for kind,platform,velocity,dt in itertools.product(['absent','dead','live'],[(0,0,0,0),(1,2,3,4),(-2,0,1,1)],[(0,0,0,1),(1,2,3,1),(-1,-2,-3,1)],[0,.125,2]):
 g=TransitionGraph();g.put(PLATFORM+0xac,'<4f',*platform);g.put(P+0x34,'<4f',*velocity);g.put(P+0x44,'<f',1.5);g.put(P+0x80,'<f',dt)
 if kind=='absent':g.put(GATE+0x18,'<I',0)
 elif kind=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 g.run([call(0x52ab90,P,[P+0x34,P+0x44])]*2,f'leave platform/{kind}/{platform}/{velocity}/{dt}')
for velocity_offset,vertical_offset in itertools.product([0x34,0x1888,0x188c,0x1890],[0x44,0x34,0x1888,0x188c]):
 g=TransitionGraph();g.put(PLATFORM+0xac,'<4f',1,2,3,4);g.put(P+velocity_offset,'<4f',2,-1,3,1);g.put(P+vertical_offset,'<f',.25)
 g.run([call(0x52ab90,P,[P+velocity_offset,P+vertical_offset])],f'leave platform overlapping outputs/{velocity_offset}/{vertical_offset}')
# Finite and signed-zero direction/angle boundaries, including overlapping copies.
for facing,direction,weight in itertools.product([(1,0,0,1),(0,0,1,1),(-1,0,-.001,1),(-1,0,.001,1),(0,0,-1,1),(-0.0,0,-0.0,1)],[(1,2,0,1),(0,0,1,1),(-1,0,-.001,1),(-1,0,.001,1),(0,0,-1,1)], [0,0x3f800000]):
 g=TransitionGraph();g.put(P+0x48,'<4f',*facing);g.put(P+0x84,'<4f',*direction)
 g.run([call(0x527720,P,[P+0x84,weight])]*2,f'prepare facing/{facing}/{direction}/{weight}')
for source_offset in [0x48,0x1918,0x191c,0x1920,0x192c,0x1930]:
 g=TransitionGraph();g.put(P+source_offset,'<4f',1,2,3,4);g.run([call(0x527720,P,[P+source_offset,0xaabbccdd])],f'prepare facing overlap/{source_offset}')
for facing,octant,out in itertools.product([(1,0,0,1),(0,0,1,1),(2,3,-4,5),(1e-30,0,-1e-30,1)],[0,1,2,3,4,5,6,7,8,0xffffffff,0x7fffffff],[P+0x84,P+0x48,P+0x44]):
 g=TransitionGraph();g.put(P+0x48,'<4f',*facing);g.run([call(0x528220,P,[out,octant])],f'probe direction/{facing}/{octant}/{out}')
RAIL,NODE,NEXT,PHYSICS=P+0x9000,P+0x9100,P+0x9200,P+0xa000
for changed,q,output in itertools.product([0,1,255],[(0,0,0,1),(0,0,0,0),(1,2,3,4),(.5,-.5,.5,-.5)],[P+0xb000,NODE+0x30,RAIL]):
 g=TransitionGraph();g.put(RAIL,'<16f',1,0,0,0,0,0,1,0,0,-1,0,0,2,3,4,1);g.put(RAIL+0x50,'<B',changed);g.put(NODE+0x30,'<4f',*q)
 g.run([call(0x57cfb0,RAIL,[output,NODE])],f'rail orientation/{changed}/{q}/{output}')
for changed,next_,position,previous in itertools.product([0,1],[0,1],[(3,4,0,1),(0,0,0,1),(1e-10,2e-10,-1e-10,1)],[0,1,3]):
 g=TransitionGraph();g.put(RAIL,'<16f',1,0,0,0,0,0,1,0,0,-1,0,0,2,3,4,1);g.put(RAIL+0x50,'<B',changed)
 g.put(NODE+0x20,'<4f',0,0,0,1);g.put(NEXT+0x20,'<4f',*position);g.put(NODE+0x40,'<2I',NEXT if next_ else 0,0 if next_ else NEXT)
 g.put(P+0x1764,'<I',NODE);g.put(P+0x176c,'<I',RAIL);g.put(P+0x178c,'<I',PHYSICS);g.put(P+0x18,'<I',previous)
 g.parameters(overrides={0x5296e3fd:40,0xac96d24b:.175});g.run([call(0x4410c0,P)]*2,f'enter rail/{changed}/{next_}/{position}/{previous}')
# Near-vertical rail exit/entry targets, facing gates, actual static/moving obstacles.
for endpoint in [(0,100,0,1),(1,100,0,1),(10,1,0,1),(0,-100,0,1),(0,0,0,1)]:
 for out in [P+0xb000,NODE+0x20,RAIL+0x20]:
  g=TransitionGraph();g.put(NODE+0x20,'<4f',0,0,0,1);g.put(NEXT+0x20,'<4f',*endpoint)
  g.run([call(0x441260,args=[NODE+0x20,NEXT+0x20,RAIL,out])],f'rail exit target/{endpoint}/{out}')
for endpoint,facing,obstacle in itertools.product([(0,100,0,1),(1,100,0,1),(10,1,0,1),(0,-100,0,1),(0,0,0,1)],[(0,0,1,1),(0,0,-1,1),(1,0,0,1)],['empty','wall','moving wall']):
 g=TransitionGraph();g.put(P+0x24,'<4f',0,0,20,1);g.put(P+0x48,'<4f',*facing);g.put(NODE+0x20,'<4f',0,0,0,1);g.put(NEXT+0x20,'<4f',*endpoint)
 if obstacle!='empty':
  actor,_=g.wall(moving=obstacle=='moving wall');g.put(g.word(g.word(actor+12)+12)+6,'<2H',1,2)
 g.run([call(0x4418b0,P,[NODE+0x20,NEXT+0x20,RAIL,P+0xb000,Q])]*2,f'rail entry target/{endpoint}/{facing}/{obstacle}')
for count,entering,shape,changed in itertools.product([0,1,3],[0,1],['valid','flag missing','far X','far Z','far Y','outside radius','reversed','previous link'],[0,1]):
 g=TransitionGraph();nodes=g.rail_nodes(count,entering,changed);g.put(P+0x24,'<4f',0,0,20,1);g.put(P+0x48,'<4f',0,0,1,1)
 for node in nodes:
  if shape=='flag missing':g.put(node+0x48,'<I',4 if node==nodes[0] else 0x20)
  elif shape.startswith('far '):g.put(node+{'far X':0x20,'far Z':0x28,'far Y':0x24}[shape],'<f',500)
  elif shape=='outside radius':g.put(node+0x20,'<3f',45,0,65)
  elif shape=='reversed':g.put(g.word(node+0x40)+0x24,'<f',-100 if entering else 200)
  elif shape=='previous link':g.put(node+0x40,'<2I',0,g.word(node+0x40))
 g.run([call(0x57d880,RAIL,[P+0x24,bits(50),bits(200),entering,P,P+0xb000,P+0xb040,Q])],f'find rail/{count}/{entering}/{shape}/{changed}')
for blocked,forced,scenario in itertools.product([0,1,255],[0,1,256,257],['empty','valid','facing away','wall','moving wall','reversed']):
 g=TransitionGraph();nodes=g.rail_nodes(0 if scenario=='empty' else 2);g.put(STATE+0x70,'<B',blocked);g.put(P+0x24,'<4f',0,0,20,1);g.put(P+0x48,'<4f',0,0,-1 if scenario=='facing away' else 1,1)
 if scenario in ['wall','moving wall']:
  actor,_=g.wall(moving=scenario=='moving wall');g.put(g.word(g.word(actor+12)+12)+6,'<2H',1,2)
 if scenario=='reversed':
  for node in nodes:g.put(g.word(node+0x40)+0x24,'<f',-100)
 g.run([call(0x441de0,P,[forced,Q])]*2,f'try rail/{blocked}/{forced}/{scenario}')
# Explicit search -> stored callback-target sequences; this does not emulate
# the intervening unrecovered animation/movement frame.
rail_sequences=[]
for rotation,forced,contact in itertools.product(['identity','quarter','half'],[0,1],[False,True]):
 g=TransitionGraph();nodes=g.rail_nodes(2,True,rotation!='identity');g.put(P+0x24,'<4f',0,0,20,1)
 if rotation=='quarter':g.put(RAIL,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,2,3,4,1);facing=(1,0,0,1)
 elif rotation=='half':g.put(RAIL,'<16f',-1,0,0,0,0,1,0,0,0,0,-1,0,2,3,4,1);facing=(0,0,-1,1)
 else:facing=(0,0,1,1)
 g.put(P+0x48,'<4f',*facing)
 if not contact:g.put(GATE+0x18,'<I',0)
 stages=g.run([call(0x441de0,P,[forced,Q]),call(0x4410c0,P)],f'rail entry and callback target/{rotation}/{forced}/{contact}')
 assert stages[0]['result']==1 and oracle.word(P+0x1948)==0x4410c0 and oracle.word(P+0x18)==3
 assert oracle.word(P+0x1764)==nodes[-1] and oracle.word(PHYSICS+0x22c)==nodes[-1]
 rail_sequences.append({'rotation':rotation,'forced':forced,'contact':contact,'selected_node':nodes[-1],'callback':'0x4410c0','final_state':3})
scope='Eleven complete original routines recover Walk gravity selection, state changes and buffered-input timing, moving-platform velocity transfer, facing preparation, indexed collision-ray direction, rail quaternion/world orientation, vertical-rail entry/exit targets, reverse node selection, entry setup and the transition callback target. Actual gameplay flags, QB/math/timing, collision queries and moving-contact cleanup execute. Twelve explicit search-to-callback-target sequences verify selection and state3 initialization, while the intervening animation/movement frame remains unrecovered. Whole arena/globals and preserved registers compare without numeric or byte allowances. Initialized graphs, valid rail links/counts and finite numeric fixtures are contracts. Three success-path reference cleanup instructions are unreachable because a false collision-query result guarantees a null moving reference. Full ground/Walk updates, remaining startup/rendering and original playable training remain unfinished.'
saved=coverage.copy();coverage.clear();finish('walk-transition',scope,{},extra);coverage.update(saved)
p=folder/'walk-transition-original.json';report=json.loads(p.read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()};report['rail_sequence_records']=rail_sequences
exclusions=json.loads((folder/'walk-transition-exclusions.json').read_text())
for at,row in report['instruction_coverage'].items():
 row['excluded']=exclusions.get(at,{})
 assert set(row['missing'])==set(row['excluded']),(at,row)
p.write_text(json.dumps(report,indent=2)+'\n')
(folder/'walk-transition-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');print(json.dumps(report['instruction_coverage']))
