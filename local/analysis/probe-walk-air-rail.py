"""Compare original airborne rail catches with real geometry and contact release."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved rail and collision graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x57c500,61,'thug_rail_catch_copy_draft',1,'word',False,False,True),
 (0x4413e0,672,'thug_walk_air_rail_target_draft',6,'byte',False,False,True),
 (0x57da20,894,'thug_walk_air_rail_search_draft',5,'byte',False,False,True),
 (0x442170,261,'thug_walk_air_rail_draft',2,'byte',True,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
functions['0x4413e0']['float_args']=[4]
class AirRailGraph(GrabGraph):
 def __init__(self,lower=40,upper=12,offset=6):
  super().__init__();self.parameters(overrides={0xac96d24b:.175,0x5296e3fd:lower,0x76bf49e0:upper,0x35b3bbda:offset})
  self.symbol(0x30ce7f2c,2,bits(30));self.put(P+0x18,'<I',1);self.put(P+0x24,'<4f',0,50,20,1);self.put(P+0x68,'<4f',0,50,30,1)
  self.put(POINT,'<8f',0,50,30,1,0,50,-10,1);self.put(NORMAL,'<4f',0,50,0,1)
  self.put(NODE+0x20,'<4f',0,0,0,1);self.put(NEXT+0x20,'<4f',0,100,0,1)
  self.put(TARGET,'<9I',*[0x11110000+i for i in range(9)]);self.put(TARGET+64,'<I',0xdeadbeef)
 def rails(self,positions=None,links=None,flags=None):
  positions=positions or [(0,0,0),(0,100,0)];links=links or [(1,None),(None,0)]
  nodes=ledge_nodes(self,positions,links,flags or [0x24]*len(positions))
  for node in nodes:self.put(node+0x30,'<4f',0,0,0,1)
  return nodes
 def target(self,out=TARGET):return call(0x4413e0,P,[NODE+32,NEXT+32,RAIL,NORMAL,bits(.5),out,Q])
 def search(self):return call(0x57da20,RAIL,[POINT,POINT+16,P,TARGET,TARGET+64,Q])
 def catch(self):return call(0x442170,P,[POINT,POINT+16,Q])
records=[]
def run(g,label,calls,changes=None):
 stages=run_grab(g,calls,label,changes)
 records.append({'label':label,'results':[s['result'] for s in stages],'state':oracle.word(P+0x18),'rail':oracle.word(P+0x1764),'selected':oracle.word(TARGET+64),'contact':oracle.word(GATE+0x18),'queries':len(trace)})
 return stages
for alignment,offset in itertools.product([0,1,4],[-36,-4,0,4,20,32,36]):
 g=AirRailGraph();at=P+0xf000+alignment;g.put(at,'<9I',*[0x11223344+i*0x10101 for i in range(9)])
 run(g,f'forward copy {alignment}/{offset}',[call(0x57c500,at+offset,[at])])
for end in [(0,100,0,1),(10,100,0,1),(10.1,100,0,1),(0,-100,0,1),(0,0,0,1),(0,100,10,1),(0,100,10.1,1),(1e-30,1e-28,0,1)]:
 for height in [39.999996,40,50,88,88.000008]:
  g=AirRailGraph();g.put(NEXT+0x20,'<4f',*end);g.put(NORMAL+4,'<f',height)
  run(g,f'target slope/height {end}/{height}',[g.target()])
for state,offset,fraction in itertools.product([0,1,2],[-6,0,6],[0,.25,1]):
 g=AirRailGraph(offset=offset);g.put(STATE+0xa0,'<B',state)
 run(g,f'target flag/offset/fraction {state}/{offset}/{fraction}',[call(0x4413e0,P,[NODE+32,NEXT+32,RAIL,NORMAL,bits(fraction),TARGET,Q])]*2,{0x7d1ec8:0xffffffff,0x696d60:1})
for axis,moving,reverse in itertools.product(['x','z'],[False,True],[False,True]):
 g=AirRailGraph();g.obstacle(axis,4,moving,reverse)
 if axis=='x':g.put(P+0x24,'<4f',20,50,0,1);g.put(RAIL+0x20,'<4f',1,0,0,0)
 run(g,f'target real obstacle {axis}/{moving}/{reverse}',[g.target()]*2)
for out in [NORMAL,NORMAL+4,RAIL+0x20,RAIL+0x24,NODE+0x20,NEXT+0x20]:
 g=AirRailGraph();run(g,f'target overlapping output {out:x}',[g.target(out)])
for shape in ['valid','empty','negative count','flag20 missing','flag4 missing','terminal','x low','x high','y low','y high','z low','z high','outside radius','slope','reversed','parallel','degenerate']:
 g=AirRailGraph();positions=[(0,0,0),(0,100,0)]
 if shape[0] in 'xyz' and ' ' in shape:
  axis='xyz'.index(shape[0]);offset=-200 if shape.endswith('low') else 200;positions=[tuple(v+(offset if j==axis else 0) for j,v in enumerate(p)) for p in positions]
 if shape=='outside radius':positions=[(25,0,30),(25,100,30)]
 if shape=='slope':positions[1]=(100,100,0)
 if shape=='reversed':positions.reverse()
 if shape=='degenerate':positions[1]=positions[0]
 nodes=g.rails(positions)
 if shape in ['empty','negative count']:g.put(RAIL+0x48,'<i',0 if shape=='empty' else -1)
 if shape=='flag20 missing':g.put(nodes[0]+0x48,'<I',4)
 if shape=='flag4 missing':g.put(nodes[0]+0x48,'<I',0x20)
 if shape=='terminal':g.put(nodes[0]+0x40,'<I',0)
 if shape=='parallel':g.put(POINT,'<8f',0,20,5,1,0,80,5,1)
 run(g,'search '+shape,[g.search()])
for first,second,bias in itertools.product([0,2,5],[0,2,5],['none','first','first endpoint','second']):
 g=AirRailGraph();nodes=g.rails([(first,0,0),(first,100,0),(second,0,0),(second,100,0)],[(1,None),(None,0),(3,None),(None,2)])
 if bias!='none':g.put(nodes[{'first':0,'first endpoint':1,'second':2}[bias]]+0x4c,'<I',0xf5b17b09)
 run(g,f'nearest and weighted {first}/{second}/{bias}',[g.search()])
for changed,angle,radius in itertools.product([0,1],[-.5,0,.5],[0,2,30]):
 import math
 g=AirRailGraph();nodes=g.rails();g.put(RAIL+0x50,'<B',changed);g.symbol(0x30ce7f2c,2,bits(radius))
 g.put(nodes[0]+0x30,'<4f',0,math.sin(angle),0,math.cos(angle));g.put(RAIL,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,5,7,9,1)
 run(g,f'search orientation {changed}/{angle}/{radius}',[g.search()])
for previous,contact,flag in itertools.product([0,1,2,3,4],['absent','dead','live'],[0,1]):
 g=AirRailGraph();nodes=g.rails();g.put(P+0x18,'<I',previous);g.put(STATE+0xa0,'<B',flag)
 if contact=='absent':g.put(GATE+0x18,'<I',0)
 if contact=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 stages=run(g,f'catch state/contact/flag {previous}/{contact}/{flag}',[g.catch()]*2)
 assert stages[0]['result']==1 and oracle.word(P+0x18)==3 and oracle.word(P+0x1764)==nodes[0]
for kind in ['empty','blocked','moving blocked','reversed']:
 g=AirRailGraph();g.rails([(0,100,0),(0,0,0)] if kind=='reversed' else None)
 if kind=='empty':g.put(RAIL+0x48,'<I',0)
 if 'blocked' in kind:g.obstacle('z',4,kind=='moving blocked',True)
 run(g,'catch '+kind,[g.catch()]*2)
scope='Four complete airborne rail-catch routines: exact forward target copy, slope/height/path eligibility, weighted closest-segment search and direct state3 transition with moving-contact release. Full airborne movement and playable training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'native_callbacks':[{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-air-rail',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-rail-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-rail-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-rail-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
