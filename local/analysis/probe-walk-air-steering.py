"""Original airborne steering with real script parameters and exact float bytes."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-ground.py').read_text().split("for kind in ['absent'")[0],'<preserved Walk graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x526850,847,'thug_walk_air_steering_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
class AirSteeringGraph(GroundGraph):
 def __init__(self):
  super().__init__();self.parameters(overrides={0x896c8888:20,0xf085443b:4})
  self.put(P+0x1878,'<4f',0,0,1,1);self.put(P+0x1888,'<4f',0,0,0,0);self.put(P+0x1898,'<f',0)
  self.put(P+0x34,'<4f',2,0,3,1);self.put(P+0x84,'<4f',1,0,0,1);self.put(P+0x94,'<f',1);self.put(P+0x80,'<f',.125)
for timer,dt in itertools.product([-.1,0,.01,.125,1],[0,.01,.125,1]):
 g=AirSteeringGraph();g.put(P+0x1898,'<f',timer);g.put(P+0x80,'<f',dt)
 g.run([call(0x526850,P)]*3,f'air input lock/{timer}/{dt}')
for basis,velocity,direction,amount,locked in itertools.product([(0,0,1,1),(.6,0,.8,1)],[(0,0,-5,1),(0,0,0,1),(0,0,30,1)],[(0,0,-1,1),(1,0,0,1),(0,0,1,1)],[0,.5,1],[0,1]):
 g=AirSteeringGraph();g.put(P+0x1878,'<4f',*basis);g.put(P+0x34,'<4f',*velocity);g.put(P+0x84,'<4f',*direction);g.put(P+0x94,'<f',amount);g.put(P+0x1958,'<B',locked)
 g.run([call(0x526850,P)]*2,f'air steering gates/{basis}/{velocity}/{direction}/{amount}/{locked}')
rng=random.Random(0x526850)
for i in range(64):
 g=AirSteeringGraph();g.parameters(overrides={0x896c8888:rng.choice([0,4,20,80]),0xf085443b:rng.choice([0,.5,4,12])})
 for offset in [0x1878,0x1888,0x34,0x84]:g.put(P+offset,'<4f',*[rng.uniform(-4,4) for _ in range(3)],rng.choice([0,1]))
 g.put(P+0x94,'<f',rng.choice([-1,0,.37,1]));g.put(P+0x1958,'<B',i%2);g.put(P+0x80,'<f',rng.choice([0,.01,.125,1]))
 g.run([call(0x526850,P)]*3,f'air steering finite vectors/{i}')
scope='Complete candidate airborne steering with input lock, sideways/forward response, preserved momentum and inherited velocity. The full airborne handler and playable training remain unfinished.'
saved=coverage.copy();coverage.clear();finish('walk-air-steering',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-steering-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-steering-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-steering-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
