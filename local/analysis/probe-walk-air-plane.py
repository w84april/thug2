"""Original airborne plane helper; real script parameter lookups and vector calls."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-ground.py').read_text().split("for kind in ['absent'")[0],'<preserved Walk graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x527c50,349,'thug_walk_air_plane_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
for enabled,height,distance,velocity in itertools.product([0,1,255],[-1,0,1],[-3,-2,-1,0,1],[(0,0,3,1),(4,0,0,1)]):
 g=GroundGraph();g.parameters(overrides={0xa20c43b7:2,0x4d16f37d:4})
 g.put(P+0x18b0,'<B',enabled);g.put(P+0x18b4,'<4f',1,0,0,1);g.put(P+0x18c4,'<2f',0,height)
 g.put(P+0x24,'<4f',distance,0,3,1);g.put(P+0x34,'<4f',*velocity);g.put(P+0x80,'<f',.125)
 g.run([call(0x527c50,P)]*2,f'air plane gates/{enabled}/{height}/{distance}/{velocity}')
rng=random.Random(0x527c50)
for i in range(64):
 g=GroundGraph();g.parameters(overrides={0xa20c43b7:rng.choice([0,1,20]),0x4d16f37d:rng.choice([-4,0,4,80])})
 g.put(P+0x18b0,'<B',1);g.put(P+0x18b4,'<4f',*[rng.uniform(-1,1) for _ in range(3)],rng.choice([0,1]))
 g.put(P+0x18c4,'<2f',rng.uniform(-3,3),100)
 for offset in [0x24,0x34]:g.put(P+offset,'<4f',*[rng.uniform(-8,8) for _ in range(3)],rng.choice([0,1]))
 g.put(P+0x80,'<f',rng.choice([0,.01,.125,1]))
 g.run([call(0x527c50,P)]*3,f'air plane finite vectors/{i}')
scope='Complete candidate airborne plane correction; full airborne dispatcher and playable training remain unfinished.'
saved=coverage.copy();coverage.clear();finish('walk-air-plane',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-plane-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-plane-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-plane-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
