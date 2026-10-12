"""Original complete ground/air frame sequences through the common Walk loop."""
from pathlib import Path
import ast
exec(compile(Path('local/analysis/probe-walk-ground-frame.py').read_text().split('\nrecords=[]')[0],'<preserved full-frame graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();frame_hits.clear()
bind(0x52d4b0,'thug_walk_update_air_prefix_draft',0,'void',True,True)
tree=ast.parse((folder/'probe-walk-air-frame.py').read_text())
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='air_parameters' for x in n.targets))
exec(compile(ast.Module(body=[assignment],type_ignores=[]),'<air parameter fixture>','exec'))
frame_states=[]
def air_update_observe(cpu,at,size,user):
 global source_probe,source_undefined
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x417760 and oracle.word(sp)==0x52a728:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
 elif at==0x52d67e and oracle.word(sp)==oracle.stop:
  frame_states.append({'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'position':bytes(cpu.mem_read(P+0x24,16)).hex(),'owner_position':bytes(cpu.mem_read(OBJ+0x4c,16)).hex(),'vertical_velocity':oracle.word(P+0x44)})
for at in [0x417760,0x52d67e]:oracle.cpu.hook_add(UC_HOOK_CODE,air_update_observe,begin=at,end=at)
source=(folder/'probe-walk-ground-frame.py').read_text()
source=source[source.index('def frame_debug'):source.index('CAM=P+')].replace("b'WALKING_GROUND, within moving object'","b'WALKING_GROUND, within moving object',b'WALKING_AIR, within moving object'")
exec(compile(source,'<air common diagnostic observer>','exec'))
class AirUpdateGraph(GroundFrameGraph):
 def __init__(self,local=True,height=20,vertical=0,speed=3):
  super().__init__(local=local,speed=speed)
  self.parameters(overrides={**air_parameters,0x1a47ffab:2,0x0ab2db54:4,0xb32c972b:4,0x0f22c135:3,0xb0675803:1,0x9b3388fa:2,0x4676a268:10,0x3fb31dfc:.25,0xc0491d2e:200})
  self.symbol(0x801c9cb6,2,bits(100));self.symbol(0x30ce7f2c,2,bits(80))
  for key in [0xd5349cc6,0x82135dd7,0x4c2b6df3]:self.symbol(key,2,bits(0))
  self.put(P+0x18,'<I',1);self.put(OBJ+0x4c,'<4f',0,height,0,1);self.put(OBJ+0xac,'<4f',0,vertical,speed,0)
  self.put(P+0x1878,'<4f',0,0,1,1);self.put(P+0x189c,'<4f',0,0,0,1);self.put(P+0x18ac,'<f',1000)
records=[]
def run(g,label,frames=12,changes=None):
 frame_states.clear();commands.clear();speed_calls.clear()
 stages=g.run([call(0x52d4b0,P,[Q])]*frames,label,{0x7cce14:NET,0x7d1ec8:1000,0x684fc8:bits(6),**(changes or {})})
 assert len(frame_states)==len(stages),(label,len(stages),len(frame_states))
 records.append({'label':label,'frames':list(frame_states),'commands':list(commands),'speed_calls':list(speed_calls),'callbacks':oracle.word(CBSTATE),'diagnostics':oracle.word(DLOG)})
 return stages
for moving,local,height,vertical,speed in itertools.product([False,True],[False,True],[2,20,80],[-40,40],[0,12]):
 g=AirUpdateGraph(local,height,vertical,speed);g.plane(0,moving=moving,half=1024,flags=0x20)
 run(g,f'fall land continue {moving}/{local}/{height}/{vertical}/{speed}')
 assert frame_states[-1]['state']==0 and all(x['position']==x['owner_position'] for x in frame_states)
 assert any(x['state']==1 for x in frame_states) or height==2
for angle,network,moving in itertools.product([-.7,0,.7],[False,True],[False,True]):
 g=AirUpdateGraph(height=30,vertical=30);g.plane(0,moving=moving,half=1024,flags=0x20)
 g.put(CAMERA+0x6c,'<16f',-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1);g.put(P+0x70c,'<B',0);g.put(P+0x710,'<I',0)
 g.put(INPUT+0x24c,'<f',1);g.put(INPUT+0x248,'<f',angle);g.put(NET,'<I',4 if network else 0)
 run(g,f'input during air and ground {angle}/{network}/{moving}')
 assert frame_states[-1]['state']==0 and frame_states[-1]['position']!=frame_states[0]['position']
for moving,mutation in itertools.product([False,True],['observe','cancel','position','velocity']):
 g=AirUpdateGraph(height=10,vertical=-100);actor,owner=g.plane(0,moving=moving,half=1024,flags=0x40)
 g.trigger(mutation,g.word(actor+4))
 if moving:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 run(g,f'landing callback through common frame {moving}/{mutation}',3)
 assert oracle.word(CBSTATE)>0
for present,ceiling,moving in itertools.product([False,True],[False,True],[False,True]):
 g=AirUpdateGraph(height=10,vertical=100)
 if present:g.plane(0,moving=moving,half=1024)
 if ceiling:g.plane(30,moving=moving,up=False,half=1024)
 run(g,f'air fallback and ceiling {present}/{ceiling}/{moving}',3)
scope='Complete original52d4b0 ground/air/animation paths with connected52cef0 and repeated air-to-ground frames, live input, landing cancellation, owner pose, shadow/light, events, animation and camera. Hanging/rail state handlers remain explicit boundaries; this partial dispatcher earns no routine count. Browser training remains unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],
 'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000],
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
finish('walk-air-update',scope,{},extra)
report=json.loads((folder/'walk-air-update-original.json').read_text());report['records']=records
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['partial_frame']={'address':'0x52d4b0','covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not frame_hits[i.address]],'completed_calls':sum(len(x['frames']) for x in records),'recovered_routine':False}
(folder/'walk-air-update-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['partial_frame'])
