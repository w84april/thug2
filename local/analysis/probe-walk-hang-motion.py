"""Original ledge corner and sideways movement with collision rollback."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved ledge geometry and collision graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x5250a0,60,'thug_walk_hang_reset_orientation_draft',0,'void',False,False,True),(0x43dfc0,612,'thug_walk_hang_corner_draft',3,'void',False,False,True),(0x440130,1368,'thug_walk_hang_traverse_draft',1,'void',False,True,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for at in [0x43dfc0,0x440130]:functions[hex(at)]['float_args']=[0]
ORCOMP,INTERP=P+0x15000,P+0x15100
class HangMotionGraph(GrabGraph):
 def __init__(self,kind='straight',angle=0,facing=1):
  super().__init__();self.nodes=self.rail(kind,angle);self.put(GATE+0x18,'<I',0);self.put(P+0x18,'<I',2)
  self.put(P+0x1760,'<I',ORCOMP);self.put(P+0x1764,'<2I',*self.nodes[:2]);self.put(P+0x18cc,'<f',.5);self.put(P+0x18dc,'<f',10)
  self.image[ORCOMP-BASE:INTERP-BASE+0x80]=bytes(INTERP-ORCOMP+0x80);self.put(ORCOMP+0x90,'<I',INTERP);self.put(ORCOMP+0xa0,'<I',P)
  self.put(INTERP+0x18,'<4I',1,bits(.1),bits(.2),bits(.3));self.put(P+0x48,'<4f',0,0,facing,1);self.put(P+0x71c,'<4f',0,0,8*facing,1)
records=[]
def run(g,calls,label):
 stages=run_grab(g,calls,label);records.append({'label':label,'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'nodes':[oracle.word(P+0x1764),oracle.word(P+0x1768)],'fraction':oracle.word(P+0x18cc),'orientation_reset':oracle.word(ORCOMP+0x1c)&255,'queries':len(trace)});return stages
for flag in [0,1,0xa5,255]:
 g=HangMotionGraph();g.put(ORCOMP+0x1c,'<B',flag);g.put(P+0x70c,'<B',flag);run(g,[call(0x5250a0,ORCOMP)]*2,f'orientation reset {flag}')
for reverse,distance,angle,facing,transformed in itertools.product([0,1,255],[0,10,90],[-1.2,0,.7],[1,-1],[False,True]):
 import math
 g=HangMotionGraph(facing=facing);g.put(g.nodes[1]+0x20,'<4f',-30+60*math.cos(angle),8,60*math.sin(angle),1);g.put(SIDE,'<4f',-60,0,0,0)
 if transformed:g.put(RAIL,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,10,20,30,1);g.put(RAIL+0x50,'<B',1)
 run(g,[call(0x43dfc0,P,[bits(distance),reverse,SIDE])]*2,f'corner {reverse}/{distance}/{angle}/{facing}/{transformed}')
for fraction,step,kind,facing in itertools.product([0,.1,.5,.9,1],[-90,-10,0,10,90],['straight','disconnected','corner'],[1,-1]):
 g=HangMotionGraph('straight' if kind=='corner' else kind,1.2 if kind=='corner' else 0,facing);g.put(P+0x18cc,'<f',fraction);g.put(P+0x24,'<4f',-30+60*fraction,-60,20,1)
 run(g,[call(0x440130,P,[bits(step),Q])],f'traverse {fraction}/{step}/{kind}/{facing}')
for axis,distance,moving,reverse in itertools.product(['x','z'],[-8,-4,4,8],[False,True],[False,True]):
 g=HangMotionGraph();g.obstacle(axis,distance,moving,reverse);run(g,[call(0x440130,P,[bits(10),Q])]*2,f'traverse obstacle {axis}/{distance}/{moving}/{reverse}')
for reverse in [0,1]:
 g=HangMotionGraph();g.put(g.nodes[1]+0x20,'<4f',-30,60,0,1);run(g,[call(0x43dfc0,P,[bits(10),reverse,SIDE])],f'vertical degenerate facing {reverse}')
for step,moving,height in itertools.product([-90,90],[False,True],[5,10,20]):
 g=HangMotionGraph('straight',1.2);g.put(P+0x720,'<f',100);g.plane(height,moving=moving,half=256)
 run(g,[call(0x440130,P,[bits(step),Q])],f'corner critical sweep rollback {step}/{moving}/{height}')
scope='Candidate complete ledge orientation reset5250a0, corner traversal43dfc0 and sideways movement440130 with real side probes, connected rails and collision rollback. Full hanging frame integration remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','native_callbacks':[{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]}]}
saved=coverage.copy();coverage.clear();finish('walk-hang-motion',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-hang-motion-original.json').read_text());report['records']=records;report['probe_traces']=probe_traces
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-hang-motion-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');(folder/'walk-hang-motion-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
