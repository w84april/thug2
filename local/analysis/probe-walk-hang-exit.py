"""Original ledge climb-up target, clearance and QB completion callbacks."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-rail-frame.py').read_text().split('for at,moving,height,facing')[0],'<preserved rail exit graph and original-write provenance>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x43db00,142,'thug_walk_hang_ground_finish_draft',0,'void',True,True,True),(0x43db90,106,'thug_walk_hang_air_finish_draft',0,'void',True,True,True),(0x43e530,1604,'thug_walk_hang_climb_draft',1,'byte',False,False,True)]
for row in specs:bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for row in extra_roots:bind(*row)
function_exports.extend([[0x43db00,'thug_walk_hang_ground_finish_draft'],[0x43db90,'thug_walk_hang_air_finish_draft']])
previous_hooks=entries|returns
entries={x[0] for x in specs+extra_roots};returns=set()
for at in entries:
 for ins in Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,0x3000),at):
  if ins.mnemonic=='int3':break
  if ins.mnemonic=='ret':returns.add(ins.address)
for at in (entries|returns)-previous_hooks:oracle.cpu.hook_add(UC_HOOK_CODE,rail_root,begin=at,end=at)
def hang_floor_source(cpu,at,size,user):
 global source_probe,source_undefined
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==0x43e55d:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
oracle.cpu.hook_add(UC_HOOK_CODE,hang_floor_source,begin=0x417760,end=0x417760)
parameters={**parameters,0xa20c43b7:8,0x9b2818cf:15,0x21dfbe77:20,0xa8c13e74:60}
class HangExitGraph(RailFrameGraph):
 def __init__(self):
  super().__init__();self.put(P+0x18,'<I',2);self.put(P+0x18d0,'<f',-60);self.put(P+0x24,'<4f',0,-60,0,1);self.put(OBJ+0x4c,'<4f',0,-60,0,1)
  self.put(P+0x1918,'<f',.75);self.put(TARGET,'<4f',0,0,20,1)
records.clear();probe_traces.clear()
for height,moving,facing in itertools.product([-100,-40,0,20,60,100],[False,True],[(0,0,1,1),(.6,0,.8,0)]):
 g=HangExitGraph();g.plane(height,moving=moving,half=256);g.put(P+0x48,'<4f',*facing)
 run(g,[call(0x43e530,P,[TARGET,Q]),call(0x5298d0,P)],f'hang climb and finish {height}/{moving}/{facing}')
for x,z,moving in itertools.product([-20,-12,0,12,20],[0,20],[False,True]):
 g=HangExitGraph();g.plane(0,moving=moving,half=8);g.put(TARGET,'<4f',x,0,z,1)
 run(g,[call(0x43e530,P,[TARGET,Q])],f'offset floor search {x}/{z}/{moving}')
for axis,distance,moving,reverse in itertools.product(['x','z'],[-8,-2,2,8],[False,True],[False,True]):
 g=HangExitGraph();g.obstacle(axis,distance,moving,reverse,low=-100,high=100)
 run(g,[call(0x43e530,P,[TARGET,Q])],f'climb clearance {axis}/{distance}/{moving}/{reverse}')
for moving,mutation,has_floor in itertools.product([False,True],['observe','cancel','position','probe'],[False,True]):
 g=HangExitGraph();actors=[]
 if has_floor:actor,owner=g.plane(0,moving=moving,half=256,flags=0x40);actors=[actor]
 g.scripts(actors,mutation);g.finish_script()
 run(g,[call(0x43e530,P,[TARGET,Q]),call(0x52ad10,P),call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)],f'hang climb animation QB {moving}/{mutation}/{has_floor}')
scope='Candidate complete climb-up clearance43e530 and ground/air completion43db00/43db90, including alternate floor candidates, radial sweeps, collision rejection and real QB animation completion. Full hanging frame remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'native_callbacks':[{'module':'walk-grounded-diagnostics.wasm','export':'fixture_walk_grounded_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-hang-exit',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-hang-exit-original.json').read_text());report['records']=records;report['probe_traces']=probe_traces
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-hang-exit-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n');(folder/'walk-hang-exit-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
