"""Original common frames through climbing, exit animation and resumed movement."""
from pathlib import Path
import ast
exec(compile(Path('local/analysis/probe-walk-air-update.py').read_text().split('\nrecords=[]')[0],'<preserved air/ground common frame graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();frame_hits.clear()
bind(0x52d4b0,'thug_walk_update_rail_prefix_draft',0,'void',True,True)
extra_roots=[(0x417760,'thug_collision_probe_initialize',0,'word',False,False),(0x4738e0,'thug_script_initialize',0,'word',False,False),(0x474540,'thug_script_setup',4,'void',True,True),(0x4750b0,'thug_script_execute',0,'word',True,True)]
entries={x[0] for x in extra_roots};returns=set();completion_states=[]
for row in extra_roots:
 bind(*row)
 # The preserved animation graph already observes all four root entries.
 oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=row[0],end=row[0])
 for ins in Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(row[0]-0x400000,0x3000),row[0]):
  if ins.mnemonic=='int3':break
  if ins.mnemonic=='ret':returns.add(ins.address)
def rail_extra_root(cpu,at,size,user):
 global source_probe,copy_destination,source_undefined
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at in entries and oracle.word(sp)==oracle.stop:source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at in returns and oracle.word(sp)==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words);root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
 elif at==0x417760 and oracle.word(sp)==0x441c4c:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
 elif at==0x5299e7:completion_states.append(oracle.word(P+0x18))
for at in entries|returns|{0x5299e7}:oracle.cpu.hook_add(UC_HOOK_CODE,rail_extra_root,begin=at,end=at)
for at,name in [(0x441020,'thug_walk_rail_bottom_finish_draft'),(0x441070,'thug_walk_rail_top_finish_draft'),(0x441860,'thug_walk_rail_air_finish_draft')]:function_exports.append([at,name])
tree=ast.parse((folder/'probe-walk-rail-frame.py').read_text());assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='parameters' for x in n.targets))
exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<rail parameters>','exec'))
node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RailFrameGraph')
for name in ['scripts','finish_script']:
 method=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name==name);method.name='rail_'+name;exec(compile(ast.Module(body=[method],type_ignores=[]),'<rail script fixture>','exec'))
class RailUpdateGraph(AirUpdateGraph):
 scripts=rail_scripts
 finish_script=rail_finish_script
 def __init__(self,fraction=.5,angle=0,network=False):
  super().__init__(height=fraction*100,vertical=0,speed=0)
  self.parameters(overrides={**air_parameters,**parameters,0x1a47ffab:2,0xb32c972b:4,0x0f22c135:3,0xb0675803:1,0x9b3388fa:2,0x4676a268:10,0x3fb31dfc:.25,0xc0491d2e:200})
  self.put(P+0x18,'<I',3);self.put(P+0x1c,'<I',1000);self.put(P+0x18cc,'<f',fraction);self.put(OBJ+0x4c,'<4f',0,fraction*100,-6,1)
  self.put(P+0x70c,'<B',0);self.put(P+0x710,'<I',0);self.put(INPUT+0x24c,'<f',1);self.put(INPUT+0x248,'<f',angle)
  self.put(CAMERA+0x6c,'<16f',-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1);self.put(NET,'<I',4 if network else 0)
  nodes=ledge_nodes(self,[(0,0,0),(0,100,0)],[(1,None),(None,0)],[0x24,0x24]);self.nodes=nodes
  for i,node in enumerate(nodes):self.put(node+0x4c,'<I',0x110+i)
  self.put(P+0x1764,'<I',nodes[0]);self.put(P+0x176c,'<I',RAIL);self.put(PHYSICS+0x22c,'<2I',nodes[0],RAIL)
records=[]
def run(g,calls,label):
 frame_states.clear();completion_states.clear();commands.clear();speed_calls.clear()
 stages=g.run([call(0x417760,P+0x17b4),*calls],label,{0x7cce14:NET,0x7d1ec8:0,0x696d60:1000,0x684fc8:bits(6)})
 records.append({'label':label,'calls':len(stages),'frames':list(frame_states),'completion_states':list(completion_states),'callbacks':oracle.word(CBSTATE),'state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls)})
 assert all(x['position']==x['owner_position'] for x in frame_states)
 return stages
for fraction,angle,moving,network in itertools.product([.15,.5,.85],[0,1.57079637,3.14159274],[False,True],[False,True]):
 g=RailUpdateGraph(fraction,angle,network);g.plane(0,moving=moving,half=1024,flags=0x20)
 run(g,[call(0x52d4b0,P,[Q])]*8,f'common rail frames {fraction}/{angle}/{moving}/{network}')
for up,present,moving in itertools.product([False,True],[False,True],[False,True]):
 g=RailUpdateGraph(.85 if up else .15,0 if up else 3.14159274);actors=[]
 if present:actors.append(g.plane(100 if up else 0,moving=moving,half=1024,flags=0x40)[0])
 g.scripts(actors);g.finish_script();g.put(CHANNELS+0x18,'<f',6)
 calls=[call(0x52d4b0,P,[Q])]*8+[call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)]+[call(0x52d4b0,P,[Q])]*6
 run(g,calls,f'common rail exit QB continue {up}/{present}/{moving}')
 assert any(x['state']==4 for x in frame_states) and completion_states==[int(up and not present)],(up,present,moving,completion_states)
 if not up and not present:
  # The original floor-miss path immediately finds this same nearby rail again.
  assert oracle.word(P+0x18)==4 and oracle.word(P+0x1948)==0x441190
 # Subsequent frames retain the original floor fallback and rail-reentry rules;
 # their complete state and memory snapshots are the comparison oracle.
 assert oracle.word(P+0x18) in [0,1,4]
scope='Common52d4b0 frames now include rail climbing, exit animation, real QB completion callbacks and resumed ground/air movement, with original pose, event, animation-speed and camera tails. Hanging remains an explicit boundary and the common dispatcher earns no routine count. Browser training remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],
 'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000],
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
finish('walk-rail-update',scope,{},extra)
report=json.loads((folder/'walk-rail-update-original.json').read_text());report['records']=records
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['partial_frame']={'address':'0x52d4b0','covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not frame_hits[i.address]],'completed_calls':sum(len(x['frames']) for x in records),'recovered_routine':False}
(folder/'walk-rail-update-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['partial_frame'])
