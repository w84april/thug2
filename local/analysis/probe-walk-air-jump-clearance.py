"""Original overhead-lip clearance for the remaining contact-jump parent."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-air-ceiling.py').read_text().split('\nrecords=[]')[0],'<preserved ceiling geometry>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x529160,646,'thug_walk_air_jump_clearance_draft',0,'void',False,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
branch_hits=Counter()
for address in [0x52923b,0x529319,0x529342]:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:branch_hits.update([at]),begin=address,end=address)
records=[]
for kind,speed in itertools.product(['empty','wide','narrow','moving','reversed'],[-200,0,100,200,500]):
 g=CeilingGraph();g.parameters(overrides={0x9ea1974a:48,0x48c0ac2a:60,0x06ebbab7:12,0xa5e2da58:900});g.put(P+0x44,'<f',speed);g.put(P+0x48,'<4f',0,0,1,1)
 if kind!='empty':g.plane(60,moving=kind=='moving',up=kind=='reversed',half=128 if kind=='wide' else 8)
 before=dict(branch_hits);g.run([call(0x529160,P,[Q])]*2,f'jump clearance {kind}/{speed}')
 records.append({'kind':kind,'speed':speed,'response':branch_hits[0x529342]-before.get(0x529342,0)})
for height,offset,gravity in itertools.product([48,49,60,108,109],[0,8,12,40],[0,100,900]):
 g=CeilingGraph();g.parameters(overrides={0x9ea1974a:48,0x48c0ac2a:60,0x06ebbab7:offset,0xa5e2da58:gravity});g.put(P+0x44,'<f',200);g.put(P+0x48,'<4f',0,0,1,-2)
 g.plane(height,moving=False,up=False,half=8);g.run([call(0x529160,P,[Q])],f'jump geometry {height}/{offset}/{gravity}')
for facing in [(1,0,0,0),(0,0,-1,1),(.25,.125,1,2),(1,0,1,-1),(-1,0,-1,3)]:
 g=CeilingGraph();g.parameters(overrides={0x9ea1974a:48,0x48c0ac2a:60,0x06ebbab7:12,0xa5e2da58:900});g.put(P+0x44,'<f',200);g.put(P+0x48,'<4f',*facing)
 g.plane(60,moving=False,up=False,half=8);g.run([call(0x529160,P,[Q])]*2,'jump facing '+str(facing))
scope='Unpublished complete candidate529160: two static overhead rays and ballistic lip-clearance displacement. Contact-jump parent and full airborne frame remain unfinished.'
extra={**extra,'native_callbacks':[]}
saved=coverage.copy();coverage.clear();finish('walk-air-jump-clearance',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-air-jump-clearance-original.json').read_text());report['records']=records;report['branch_hits']={hex(k):v for k,v in branch_hits.items()}
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-air-jump-clearance-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-air-jump-clearance-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'],report['branch_hits'])
