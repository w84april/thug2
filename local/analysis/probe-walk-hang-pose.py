"""Original ledge pose and drop-input helpers without gameplay stubs."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0],'<preserved rail/contact geometry>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x43da20,67,'thug_walk_hang_drop_input_draft',0,'word',False,False,True),(0x43fc70,434,'thug_walk_hang_pose_draft',0,'void',True,False,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for suppressed,amount,angle in itertools.product([0,1,0xffffffff],[0,1,-1],[-3.5,-3.14159274,-2.35619449,-1,0,1,2.35619449,3.14159274,3.5]):
 g=GrabGraph();pad=INPUT+0x20;g.put(pad+0x234,'<I',suppressed);g.put(pad+0x22c,'<f',amount);g.put(pad+0x228,'<f',angle)
 run_grab(g,[call(0x43da20,pad)],f'hang drop input {suppressed}/{amount}/{angle}')
for contact,fraction,facing,transformed in itertools.product(['none','dead','stable','rotated'],[0,.5,1],[(0,0,1,1),(0,0,-1,1),(.6,.2,.8,0)],[False,True]):
 g=GrabGraph();nodes=g.rail();g.put(P+0x1764,'<3I',nodes[0],nodes[1],RAIL);g.put(P+0x18cc,'<3f',fraction,-60,10);g.put(P+0x48,'<4f',*facing)
 if transformed:g.put(RAIL,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,10,20,30,1);g.put(RAIL+0x50,'<B',1)
 if contact=='none':g.put(GATE+0x18,'<I',0)
 elif contact=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 else:g.put(CONTACT+0xac,'<B',int(contact=='rotated'))
 run_grab(g,[call(0x43fc70,P)]*2,f'hang pose {contact}/{fraction}/{facing}/{transformed}')
scope='Candidate complete hanging drop-input43da20 and rail-relative pose43fc70, including transformed rails, dead contacts and orientation changes. Full hanging frames and browser training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','native_callbacks':[]}
saved=coverage.copy();coverage.clear();finish('walk-hang-pose',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-hang-pose-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-hang-pose-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');(folder/'walk-hang-pose-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
