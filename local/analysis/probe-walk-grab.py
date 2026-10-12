"""Original ledge side-clearance and target-selection graph."""
from pathlib import Path
source=Path('local/analysis/probe-walk-floor.py').read_text().split('for flags,progress,height')[0]
exec(compile(source,'<preserved floor prerequisite graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x43f3a0,2243,'thug_walk_hang_side_blocked_draft',11,'byte',False,True,True),
 (0x43fe30,754,'thug_walk_hang_target_draft',3,'byte',False,True,True),
 (0x440690,1372,'thug_walk_choose_ledge_draft',7,'byte',False,True,True),
 (0x57dda0,969,'thug_walk_scan_ledge_draft',6,'byte',False,True,True),
 (0x43ec40,1007,'thug_walk_try_hang_draft',0,'byte',True,True,True)]
for row in specs:bind_new(*row)
functions[hex(0x43f3a0)]['float_args']=[1,5,6,7,8]
functions[hex(0x440690)]['float_args']=[4]
functions[hex(0x57dda0)]['float_args']=[5]
bind(0x43dcf0,'thug_walk_enter_hang_draft',0,'void',True,True)
function_exports.append([0x43dcf0,'thug_walk_enter_hang_draft']);fields.add(P+0x1948)
bind(0x417760,'thug_collision_probe_initialize',0,'word',False,False)
def ledge_nodes(g,positions,links,flags=None):
 nodes=g.alloc(len(positions)*0x54);g.put(RAIL+0x40,'<3I',nodes,0,len(positions))
 for i,position in enumerate(positions):
  at=nodes+i*0x54;g.image[at-BASE:at-BASE+0x54]=bytes(0x54);g.put(at+0x20,'<4f',*position,1)
  next_,previous=links[i];g.put(at+0x40,'<3I',nodes+next_*0x54 if next_ is not None else 0,nodes+previous*0x54 if previous is not None else 0,4 if flags is None else flags[i])
 for i,position in enumerate(positions):
  next_=links[i][0];other=position if next_ is None else positions[next_]
  g.put(nodes+i*0x54,'<8f',*[min(a,b) for a,b in zip(position,other)],1,*[max(a,b) for a,b in zip(position,other)],1)
 return [nodes+i*0x54 for i in range(len(positions))]

PROBE,TARGET,SIDE,NORMAL,POINT=P+0x12000,P+0x12100,P+0x12140,P+0x12150,P+0x12160
class GrabGraph(FloorGraph):
 def __init__(self):
  super().__init__();self.parameters(overrides={0xac96d24b:.175,0xafbf7687:2,0xc3263e6e:8,0xa8c13e74:60,0xde86132e:30,0x7201ad48:.5,0x8f35f29f:12,
   0x3344a6d0:8,0x84ff931c:40,0xcbeb3d89:2,0xc774dd6d:20,0x262a9467:0,0xa85ec070:12,0x98724ebc:30,0x01d1e6af:1,0xfdc8aec0:1,0xdbb3d53e:10,0x2f83ae83:12})
  self.put(P+0x176c,'<I',RAIL);self.put(P+0x24,'<4f',0,-60,20,1);self.put(P+0x68,'<4f',0,-60,30,1);self.put(P+0x48,'<4f',0,0,1,1)
  self.symbol(0xa8276303,2,bits(80))
  self.put(NORMAL,'<4f',0,0,1,1);self.put(SIDE,'<4f',-1,0,0,1);self.put(POINT,'<4f',0,-60,0,1)
 def rail(self,kind='straight',angle=0):
  import math
  pos=[(-30,0,0),(30,0,0),(30+30*math.cos(angle),0,30*math.sin(angle)),(-30-30*math.cos(angle),0,30*math.sin(angle))]
  links=[(1,3),(2,0),(None,1),(0,None)]
  if kind=='disconnected':links=[(1,None),(None,0),(None,None),(None,None)]
  nodes=ledge_nodes(self,pos,links);self.put(TARGET,'<12f',0,0,0,1,0,0,1,1,.5,0,0,0);self.put(TARGET+48,'<I',nodes[0]);return nodes
 def obstacle(self,axis='x',distance=4,moving=False,reverse=False,low=-100,high=100):
  actor,owner=self.wall(distance,moving);geo=self.word(actor+12);verts=self.word(geo+48)
  coords=[(-64,low,distance),(64,low,distance),(0,high,distance)]
  if axis=='x':coords=[(z,y,x) for x,y,z in coords]
  self.put(verts,'<9f',*[v for point in coords for v in point]);lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)];self.put(geo+16,'<8f',*lo,1,*hi,1)
  self.put(self.word(geo+12)+6,'<2H',1 if reverse else 2,2 if reverse else 1);return actor,owner

# Original automatic-cache identities survive in the released registry slots.
for i in range(8):
 if 0x6918ec+i*4 not in index:glob('thug_collision_cache_registry',0x6918ec+i*4,0,offset=i*4)
if 0x69190c not in index:glob('thug_collision_cache_mask',0x69190c)
stack_records=[]
def observe_cache(cpu,at,size,user):
 if at!=0x40ab40:
  if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:stack_records.append([])
  return
 at=cpu.reg_read(UC_X86_REG_ECX);count=oracle.word(at+0xfc0);assert count<=500
 assert oracle.stack<=at<oracle.stack+0x20000
 slots=[i for i in range(8) if oracle.word(0x6918ec+i*4)==at and oracle.word(0x69190c)&(1<<i)]
 assert len(slots)==1,slots
 stack_records[-1].append({'original':at,'global':['thug_collision_cache_registry',slots[0]*4],'mask':['thug_collision_cache_mask',slots[0],0],'size':0xfcc,
  'blocks':[[0,bytes(cpu.mem_read(at,32)).hex()],[0xfc0,bytes(cpu.mem_read(at+0xfc0,12)).hex()],[32,bytes(cpu.mem_read(at+32,count*8)).hex(),list(range(0,count*8,4))]]})
for at in [*[r[0] for r in specs],0x43dcf0,0x417760,0x40ab40]:oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=at,end=at)
grab_base_case=case
def case(calls,patches=(),changes=None,label='Walk grab'):
 stack_records.clear();stages=grab_base_case(calls,patches,changes,label);assert len(stages)==len(stack_records)
 for stage,objects in zip(stages,stack_records):stage['stack_objects']=objects
 return stages

probe_traces=[];trace=[]
def observe_query(cpu,at,size,user):
 probe=cpu.reg_read(UC_X86_REG_ECX);trace.append({'segment':list(struct.unpack('<8f',cpu.mem_read(probe,32))),'cache':oracle.word(probe+0xac)})
oracle.cpu.hook_add(UC_HOOK_CODE,observe_query,begin=0x4172f0,end=0x4172f0)
def run_grab(g,calls,label,changes=None):
 trace.clear();stages=g.run(calls,label,changes);probe_traces.append({'label':label,'steps':[s['result'] for s in stages],'queries':len(trace),'segments':list(trace)});return stages

for side,fraction,angle,kind in itertools.product([0,1,255],[0,.05,.5,.95,1],[-.7,0,.7],['straight','disconnected']):
 g=GrabGraph();nodes=g.rail(kind,angle);run_grab(g,[call(0x43f3a0,P,[NORMAL,bits(fraction),POINT,side,SIDE,bits(-60),0,0,0,nodes[0],nodes[1],Q])],f'side clearance/empty/{side}/{fraction}/{angle}/{kind}')
for side,axis,distance,moving,reverse in itertools.product([0,1],['x','z'],[-8,-4,0,4,8],[False,True],[False,True]):
 g=GrabGraph();nodes=g.rail();g.obstacle(axis,distance,moving,reverse)
 run_grab(g,[call(0x43f3a0,P,[NORMAL,bits(.5),POINT,side,SIDE,bits(-60),0,0,0,nodes[0],nodes[1],Q])]*2,f'side clearance/obstacle/{side}/{axis}/{distance}/{moving}/{reverse}')
for height,moving,up in itertools.product([-80,-60,-40,-30,-20,-10,0,10,20],[False,True],[False,True]):
 g=GrabGraph();nodes=g.rail();g.plane(height,moving=moving,up=up)
 run_grab(g,[call(0x43f3a0,P,[NORMAL,bits(.5),POINT,0,SIDE,bits(-60),0,0,0,nodes[0],nodes[1],Q])],f'side clearance/horizontal/{height}/{moving}/{up}')
rng=random.Random(0x43f3a0)
for trial in range(24):
 g=GrabGraph();nodes=g.rail('disconnected');g.put(NORMAL,'<4f',*[rng.uniform(-2,2) for _ in range(4)]);g.put(SIDE,'<4f',*[rng.uniform(-2,2) for _ in range(4)]);g.put(POINT,'<4f',*[rng.uniform(-100,100) for _ in range(4)])
 delta=[bits(rng.uniform(-50,50)) for _ in range(4)]
 run_grab(g,[call(0x43f3a0,P,[NORMAL,bits(.5),POINT,trial%2,SIDE,*delta,nodes[0],nodes[1],Q])],f'side finite arithmetic/{trial}')
for state,shape,moving,reverse in itertools.product([0,1,2],['empty','side x','side z','floor','ceiling'],[False,True],[False,True]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state)
 if shape.startswith('side'):g.obstacle(shape[-1],4,moving,reverse)
 if shape in ['floor','ceiling']:g.plane(-30 if shape=='floor' else 5,moving=moving,up=not reverse)
 run_grab(g,[call(0x417760,PROBE)]+[call(0x43fe30,P,[PROBE,TARGET,TARGET,Q])]*2,f'hang target/{state}/{shape}/{moving}/{reverse}')
for state,height,moving,reverse in itertools.product([0,1,2],[-65,-58,-50],[False,True],[False,True]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state);g.put(POINT,'<4f',0,0,0,1);g.obstacle('z',12,moving,reverse,low=-100,high=height)
 run_grab(g,[call(0x417760,PROBE)]+[call(0x43fe30,P,[PROBE,POINT,TARGET,Q])]*2,f'hang target final path/{state}/{height}/{moving}/{reverse}')
for state,side,flags,facing in itertools.product([0,1,2],[0,1,255],[4,0x44,0x84,0xc4],[-1,1]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state);g.put(nodes[0]+0x48,'<I',flags);g.put(P+0x50,'<f',facing)
 g.put(POINT,'<4f',0,0,0,1);g.put(POINT+16,'<4f',0,0,0,1)
 run_grab(g,[call(0x440690,P,[nodes[0]+32,nodes[1]+32,POINT,POINT+16,bits(.5),TARGET,side,Q])]*2,f'choose empty/{state}/{side}/{flags}/{facing}')
for state,slope,height in itertools.product([0,1,2],[0,5,30,60],[-13,-12,0,12,13]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state);g.put(nodes[1]+36,'<f',slope)
 g.put(POINT,'<4f',0,0,0,1);g.put(POINT+16,'<4f',0,height,0,1)
 run_grab(g,[call(0x440690,P,[nodes[0]+32,nodes[1]+32,POINT,POINT+16,bits(.5),TARGET,0,Q])],f'choose height slope/{state}/{slope}/{height}')
for state,side,axis,distance,moving,reverse in itertools.product([0,1,2],[0,1],['x','z'],[-12,-4,4,12],[False,True],[False,True]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state);g.put(POINT,'<4f',0,0,0,1);g.put(POINT+16,'<4f',0,0,0,1);g.obstacle(axis,distance,moving,reverse)
 run_grab(g,[call(0x440690,P,[nodes[0]+32,nodes[1]+32,POINT,POINT+16,bits(.5),TARGET,side,Q])],f'choose obstacle/{state}/{side}/{axis}/{distance}/{moving}/{reverse}')
for flags,side,distance in itertools.product([0x44,0x84,0xc4],[0,1],[-4,4]):
 g=GrabGraph();nodes=g.rail();g.put(nodes[0]+0x48,'<I',flags);g.obstacle('x',distance);g.put(POINT,'<4f',0,0,0,1);g.put(POINT+16,'<4f',0,0,0,1)
 run_grab(g,[call(0x440690,P,[nodes[0]+32,nodes[1]+32,POINT,POINT+16,bits(.5),TARGET,side,Q])],f'choose blocked one-sided/{flags}/{side}/{distance}')
for shape,radius,direction,state in itertools.product(['valid','empty','flag20','flag8','missing flag','terminal','far x','far y','far z','outside sphere','parallel','degenerate','slope'],[2,8,80],[-1,1],[0,1]):
 g=GrabGraph();positions=[(-30,0,0),(30,0,0)];links=[(1,None),(None,0)];flags=[4,4]
 if shape=='slope':positions[1]=(30,100,0)
 if shape=='degenerate':positions[1]=positions[0]
 if shape.startswith('far '):positions=[tuple(v+(200 if j=={'far x':0,'far y':1,'far z':2}[shape] else 0) for j,v in enumerate(p)) for p in positions]
 if shape=='outside sphere':positions=[(x,5,5) for x,y,z in positions]
 if shape=='terminal':links=[(None,None),(None,None)]
 if shape in ['flag20','flag8','missing flag']:flags=[{'flag20':0x24,'flag8':0xc,'missing flag':0}[shape]]*2
 nodes=ledge_nodes(g,positions,links,flags);g.put(TARGET+48,'<I',nodes[0]);g.put(P+0x18,'<I',state)
 if shape=='empty':g.put(RAIL+0x48,'<I',0)
 g.put(POINT,'<4f',0,5,20,1);g.put(POINT+16,'<4f',0,5,-20,1);g.put(NORMAL,'<4f',0,direction,0,1)
 if shape=='parallel':g.put(POINT,'<4f',-20,5,0,1);g.put(POINT+16,'<4f',20,5,0,1)
 run_grab(g,[call(0x57dda0,RAIL,[POINT,POINT+16,NORMAL,P,TARGET,bits(radius),Q])],f'scan/{shape}/{radius}/{direction}/{state}')
for blocked,speed,hangblocked,kind in itertools.product([0,1],[0,70,71],[0,1],['fixed','empty','moving','second moving']):
 g=GrabGraph();g.rail();g.put(P+0x34,'<4f',speed,0,0,1);g.put(STATE+0x70,'<B',blocked);g.put(HANG+0x1c,'<B',hangblocked);changes={}
 if kind!='fixed':g.put(RAIL+0x48,'<I',0)
 if 'moving' in kind:
  head,component,transform,nodes=g.moving_grind(kind=='second moving')
  g.put(g.word(component+12)+4,'<I',0)
  g.put(transform,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,100,20,-50,1);g.put(transform+0x50,'<B',1)
  g.put(P+0x68,'<4f',80,-40,-50,0);g.put(P+0x24,'<4f',120,-40,-50,-2);changes[0x6f0db8]=head
 run_grab(g,[call(0x43ec40,P,[Q])],f'full grab/{blocked}/{speed}/{hangblocked}/{kind}',changes)
# A successful moving candidate may have another registry item after it.
g=GrabGraph();g.put(RAIL+0x48,'<I',0);head,component,transform,nodes=g.moving_grind();g.put(g.word(component+12)+4,'<I',0);g.put(component+0x14,'<I',head)
g.put(transform,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,100,20,-50,1);g.put(transform+0x50,'<B',1);g.put(P+0x68,'<4f',80,-40,-50,1);g.put(P+0x24,'<4f',120,-40,-50,1)
run_grab(g,[call(0x43ec40,P,[Q])],'moving success before remaining registry item',{0x6f0db8:head})
for angle,scale in itertools.product([.3,-.7,1.1],[.5,1,2]):
 import math
 g=GrabGraph();g.put(RAIL+0x48,'<I',0);head,component,transform,nodes=g.moving_grind(angle=angle,scale=scale);owner=g.word(component+12);g.put(owner+4,'<I',0)
 c,z=math.cos(angle)*scale,math.sin(angle)*scale;g.put(transform,'<16f',c,0,-z,0,0,1,0,0,z,0,c,0,100,20,-50,1);g.put(transform+0x50,'<B',1)
 g.put(P+0x68,'<4f',100-20*c,-40,-50+20*z,1);g.put(P+0x24,'<4f',100+20*c,-40,-50-20*z,1)
 run_grab(g,[call(0x43ec40,P,[Q])],f'transformed full grab/{angle}/{scale}',{0x6f0db8:head})
callback_records=[]
for mode,state,progress in itertools.product(['empty','script','mutating'],[0,2],[0,.25,1]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x18,'<I',state);g.put(nodes[0]+0x4c,'<I',0x110);g.put(ANIM+0x44,'<B',8);g.put(ANIM+0x20,'<f',progress)
 if mode!='empty':
  g.level_nodes([(0x110,[(0x2ca8a299,13,6)])]);g.callback([(P+12,ALTOWNER),(HANG+0x1d,7)] if mode=='mutating' else [])
 stages=run_grab(g,[call(0x43ec40,P,[Q]),call(0x43dcf0,P)],f'grab then explicit stored callback/{mode}/{state}/{progress}')
 assert stages[0]['result']==1 and oracle.word(P+0x18)==2 and oracle.cpu.mem_read(HANG+0x1d,1)==b'\0'
 callback_records.append({'mode':mode,'previous_state':state,'progress':progress,'selected':oracle.word(P+0x1764),'state':2,'callbacks':oracle.word(CBSTATE)})
scope='Five complete ledge-grab routines recover side/vertical/path clearance, usable-side selection, weighted segment search and fixed/moving hanging transition. Whole defined arena/global state and preserved registers compare, including automatic collision-cache identity/lifetime. Explicit stored-callback sequences reach hanging state but do not implement intervening animation frames. Full floor/ground/Walk frames, startup, rendering and original training browser playability remain unfinished.'
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-grab',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-grab-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()};report['probe_traces']=probe_traces;report['callback_records']=callback_records
(folder/'walk-grab-original.json').write_text(json.dumps(report,indent=2)+'\n');(folder/'walk-grab-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');print(json.dumps(report['instruction_coverage']))
