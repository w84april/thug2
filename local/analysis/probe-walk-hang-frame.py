"""Original full hanging frames and connected climb/drop sequences."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-hang-exit.py').read_text().split('for height,moving,facing')[0],'<preserved climb graph and retained-probe observations>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x440bf0,1059,'thug_walk_hang_frame_draft',0,'void',True,True,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for row in extra_roots:bind(*row)
previous_hooks=entries|returns;entries={x[0] for x in specs+extra_roots};returns=set()
for at in entries:
 for ins in Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,0x3000),at):
  if ins.mnemonic=='int3':break
  if ins.mnemonic=='ret':returns.add(ins.address)
for at in (entries|returns)-previous_hooks:oracle.cpu.hook_add(UC_HOOK_CODE,rail_root,begin=at,end=at)
ORCOMP,INTERP=P+0x15000,P+0x15100
parameters={**parameters,0x52fa7ca6:60,0x1b877928:45,0xd77ee881:100,0xc506a97c:8,0x228b5376:.01}
class HangFrameGraph(HangExitGraph):
 def __init__(self,angle=0,amount=1,pressed=0,dt=.125,kind='straight'):
  super().__init__();self.nodes=self.rail(kind,1.2);self.put(P+0x1764,'<2I',*self.nodes[:2]);self.put(PHYSICS+0x22c,'<2I',self.nodes[0],RAIL)
  self.put(P+0x18cc,'<3f',.5,-60,0);self.put(P+0x18dc,'<f',0);self.put(P+0x1760,'<I',ORCOMP);self.put(P+0x71c,'<4f',0,0,8,1)
  self.put(P+0x98,'<B',pressed);self.put(P+0x80,'<f',dt);self.put(P+0x94,'<f',amount);self.put(INPUT+0x248,'<2f',angle,amount);self.put(INPUT+0x250,'<2I',0,0)
  self.image[ORCOMP-BASE:INTERP-BASE+0x80]=bytes(INTERP-ORCOMP+0x80);self.put(ORCOMP+0x90,'<I',INTERP);self.put(ORCOMP+0xa0,'<I',P)
 def contact(self,kind,rotation=0):
  import math
  if kind=='none':return
  self.put(GATE+0x18,'<I',CONTACT)
  if kind=='dead':self.put(CONTACT,'<I',0);self.put(PLATFORM+4,'<I',0);return
  component=self.alloc(28);self.put(component,'<7I',0x64637c,0x1cdfb2a3,0,PLATFORM,0,0,RAIL);fields.add(component);self.put(PLATFORM+0x100,'<I',component)
  c,z=math.cos(rotation),math.sin(rotation);self.put(PLATFORM+0x6c,'<16f',c,0,-z,0,0,1,0,0,z,0,c,0,0,0,0,1);self.put(PLATFORM+0x4c,'<4f',10,20,30,1)
records.clear();probe_traces.clear()
for angle,amount,dt,kind in itertools.product([-3.14159274,-1.57079637,0,.8,1.57079637,3.14159274],[0,1],[0,.125,1],['straight','disconnected']):
 g=HangFrameGraph(angle,amount,dt=dt,kind=kind);run(g,[call(0x440bf0,P,[Q])]*3,f'hanging traversal frames {angle}/{amount}/{dt}/{kind}')
for angle,amount,suppression,shape in itertools.product([0,.7,1.6,3.14159274,-3.14159274],[0,1],['none','forward','drop'],['empty','floor','full blocked','both blocked']):
 g=HangFrameGraph(angle,amount,pressed=1)
 if suppression=='forward':g.put(INPUT+0x250,'<I',1)
 if suppression=='drop':g.put(INPUT+0x254,'<I',1)
 if shape=='floor':g.plane(0,half=256)
 elif shape.endswith('blocked'):g.obstacle('z',15 if shape=='full blocked' else 5,reverse=True)
 run(g,[call(0x440bf0,P,[Q])],f'hanging climb/drop {angle}/{amount}/{suppression}/{shape}')
for kind,rotation,angle,pressed in itertools.product(['none','dead','live'],[0,.5],[0,1.57079637,3.14159274],[0,1]):
 g=HangFrameGraph(angle,pressed=pressed);g.contact(kind,rotation);run(g,[call(0x440bf0,P,[Q])],f'moving ledge frame {kind}/{rotation}/{angle}/{pressed}')
for moving,mutation in itertools.product([False,True],['observe','cancel','position','probe']):
 g=HangFrameGraph(0,pressed=1);actor,owner=g.plane(0,moving=moving,half=256,flags=0x40);g.scripts([actor],mutation);g.finish_script()
 run(g,[call(0x440bf0,P,[Q]),call(0x52ad10,P),call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)],f'hanging climb frame QB {moving}/{mutation}')
for distance,moving,reverse in itertools.product([5,10,15,20],[False,True],[False,True]):
 g=HangFrameGraph(0,pressed=1);g.obstacle('z',distance,moving,reverse,low=-200,high=200)
 run(g,[call(0x440bf0,P,[Q])],f'climb retry barrier {distance}/{moving}/{reverse}')
scope='Candidate complete hanging440bf0 with real moving-contact transport, rail poses, input gates, two climb attempts, drop events, smoothed sideways traversal, corner turns, collision rollback and QB completion. Common-loop integration and browser training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'native_callbacks':[{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-hang-frame',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-hang-frame-original.json').read_text());report['records']=records;report['probe_traces']=probe_traces
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-hang-frame-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');(folder/'walk-hang-frame-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
