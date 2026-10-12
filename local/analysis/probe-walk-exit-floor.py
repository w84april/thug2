"""Compare real fixed/moving floor queries used by ledge and rail exits."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved collision graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind(0x417760,'thug_collision_probe_initialize',0,'word',False,False)
specs=[(0x528280,232,'thug_walk_exit_floor_draft',3,'byte',False,False,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
records=[]
for moving,height,up,aliased in itertools.product([False,True],[-100,-20,0,20,60,80],[False,True],[False,True]):
 g=GrabGraph();g.parameters(overrides={0x6da7f696:30,0xaebfa9cd:40});g.plane(height,moving=moving,up=up,half=128);g.put(POINT,'<4f',0,10,0,1)
 out=POINT if aliased else TARGET
 stages=run_grab(g,[call(0x417760,PROBE),call(0x528280,P,[POINT,out,PROBE,Q])],f'exit floor {moving}/{height}/{up}/{aliased}')
 records.append({'label':labels[-1],'hit':stages[-1]['result'],'position':bytes(oracle.cpu.mem_read(out,16)).hex()})
for height,depth,offset in itertools.product([0,1,30],[-10,0,40],[-4,0,4]):
 g=GrabGraph();g.parameters(overrides={0x6da7f696:height,0xaebfa9cd:depth});g.put(POINT,'<6I',bits(4),bits(10),bits(8),0x80000000,0x7fc12345,0)
 run_grab(g,[call(0x417760,PROBE),call(0x528280,P,[POINT,POINT+offset,PROBE,Q])],f'exit floor miss forward copy {height}/{depth}/{offset}')
scope='Complete candidate528280 exit-floor target using actual collision queries, fixed/moving surfaces and aliased output. Rail/hang frame integration remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','native_callbacks':[]}
saved=coverage.copy();coverage.clear();finish('walk-exit-floor',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-exit-floor-original.json').read_text());report['records']=records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-exit-floor-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-exit-floor-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
