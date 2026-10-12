"""Original airborne ledge catches through fixed/moving scans and real rail scripts."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved ledge graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x43f030,872,'thug_walk_air_ledge_draft',8,'byte',True,True,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
functions['0x43f030']['float_args']=list(range(8))
class AirLedgeGraph(GrabGraph):
 def __init__(self):
  super().__init__();self.symbol(0x30ce7f2c,2,bits(80));self.put(P+0x18,'<I',1);self.put(P+0x44,'<f',-10)
  self.put(P+0x1788,'<I',STATE);self.put(P+0x34,'<4f',1,0,3,1);self.put(STATE+0xa0,'<B',0)
 def sweep(self,points=None):
  points=points or (0,-60,30,1,0,-60,-10,1)
  return call(0x43f030,P,[*[bits(v) for v in points],Q])
records=[]
def run(g,label,calls=None,changes=None):
 stages=run_grab(g,calls or [g.sweep()],label,changes)
 records.append({'label':label,'results':[s['result'] for s in stages],'state':oracle.word(P+0x18),'callbacks':oracle.word(CBSTATE),'active_contact':oracle.word(GATE+0x18),'rail':oracle.word(P+0x1764)})
 return stages
for speed in [-100,0,49.999996,50,50.000004,51,100,float('nan')]:
 g=AirLedgeGraph();g.rail();g.put(P+0x44,'<f',speed);run(g,'vertical speed '+str(speed))
for kind in ['valid','empty','far','flags','terminal','facing away']:
 g=AirLedgeGraph();nodes=g.rail()
 if kind=='empty':g.put(RAIL+0x48,'<I',0)
 if kind=='far':g.put(P+0x24,'<4f',200,-60,20,1)
 if kind=='flags':
  for node in nodes:g.put(node+0x48,'<I',0x28)
 if kind=='terminal':
  for node in nodes:g.put(node+0x40,'<I',0)
 if kind=='facing away':g.put(P+0x50,'<f',-1)
 run(g,'fixed candidate '+kind)
for height,radius in itertools.product([-20,-1,0,1,12,13,100],[0,2,80]):
 g=AirLedgeGraph();g.rail();g.symbol(0x30ce7f2c,2,bits(radius));run(g,f'sweep height/radius {height}/{radius}',[g.sweep((0,height-60,30,3,0,height-60,-10,-2))])
for axis,moving,reverse in itertools.product(['x','z'],[False,True],[False,True]):
 g=AirLedgeGraph();g.rail();g.obstacle(axis,4,moving,reverse);run(g,f'clearance obstruction {axis}/{moving}/{reverse}')
for old in ['absent','dead','live']:
 g=AirLedgeGraph();g.rail()
 if old=='absent':g.put(GATE+0x18,'<I',0)
 if old=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 run(g,'release previous contact '+old,[g.sweep()]*2)
for kind in ['empty','moving','second moving','moving then another']:
 g=AirLedgeGraph();g.put(RAIL+0x48,'<I',0);changes={};points=(80,-40,-50,0,120,-40,-50,-2)
 if kind!='empty':
  head,component,transform,nodes=g.moving_grind(kind=='second moving');g.put(g.word(component+12)+4,'<I',0)
  g.put(transform,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,100,20,-50,1);g.put(transform+0x50,'<B',1)
  g.put(P+0x24,'<4f',120,-40,-50,1);changes[0x6f0db8]=head
  if kind=='moving then another':g.put(component+0x14,'<I',head)
 run(g,'moving registry '+kind,[g.sweep(points)]*2,changes)
for angle,scale in itertools.product([.3,-.7,1.1],[.5,1,2]):
 import math
 g=AirLedgeGraph();g.put(RAIL+0x48,'<I',0);head,component,transform,nodes=g.moving_grind(angle=angle,scale=scale);g.put(g.word(component+12)+4,'<I',0)
 c,z=math.cos(angle)*scale,math.sin(angle)*scale;g.put(transform,'<16f',c,0,-z,0,0,1,0,0,z,0,c,0,100,20,-50,1);g.put(transform+0x50,'<B',1)
 points=(100-20*c,-40,-50+20*z,0,100+20*c,-40,-50-20*z,-2);g.put(P+0x24,'<4f',*points[4:7],1)
 run(g,f'moving transform {angle}/{scale}',[g.sweep(points)],{0x6f0db8:head})
for mode,flag,progress in itertools.product(['empty','script','mutating'],[0,1,2],[0,.25,1]):
 g=AirLedgeGraph();nodes=g.rail();g.put(nodes[0]+0x4c,'<I',0x110);g.put(STATE+0xa0,'<B',flag);g.put(ANIM+0x44,'<B',8);g.put(ANIM+0x20,'<f',progress)
 if mode!='empty':
  g.level_nodes([(0x110,[(0x2ca8a299,13,6)])]);g.callback([(P+12,ALTOWNER),(STATE+0xa0,2)] if mode=='mutating' else [])
 stages=run(g,f'rail event {mode}/{flag}/{progress}',[g.sweep()]*2)
 assert stages[0]['result']==1 and oracle.word(P+0x18)==2
 if mode!='empty':assert oracle.word(CBSTATE)>0
scope='Complete airborne ledge catch 43f030: fixed and transformed moving ledge scans, clearance, moving-contact lifetime, immediate hanging state, model blend and real rail-script callbacks. Full airborne frames and playable training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-air-ledge',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-ledge-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-ledge-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-ledge-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
