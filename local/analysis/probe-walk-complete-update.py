"""Original complete walking dispatcher: all five movement states and transitions."""
from pathlib import Path
import ast
exec(compile(Path('local/analysis/probe-walk-rail-update.py').read_text().split('\nrecords=[]')[0],'<preserved connected frame graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();frame_hits.clear()
bind(0x52d4b0,'thug_walk_update_draft',0,'void',True,True)
for row in extra_roots:bind(*row)
for at,name in [(0x43db00,'thug_walk_hang_ground_finish_draft'),(0x43db90,'thug_walk_hang_air_finish_draft')]:function_exports.append([at,name])
def hang_source(cpu,at,size,user):
 global source_probe,source_undefined
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==0x43e55d:source_probe=cpu.reg_read(UC_X86_REG_ECX);source_undefined={0x70,0xa8}
oracle.cpu.hook_add(UC_HOOK_CODE,hang_source,begin=0x417760,end=0x417760)
for filename in ['probe-walk-hang-exit.py','probe-walk-hang-frame.py']:
 tree=ast.parse((folder/filename).read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='parameters' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<hanging parameters>','exec'))
node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='HangFrameGraph');method=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name=='contact');method.name='hang_contact';exec(compile(ast.Module(body=[method],type_ignores=[]),'<moving ledge fixture>','exec'))
class HangUpdateGraph(RailUpdateGraph):
 contact=hang_contact
 def __init__(self,angle=1.57079637,amount=1,network=False):
  super().__init__(angle=angle,network=network);self.parameters(overrides={**air_parameters,**parameters,0x1a47ffab:2,0xb32c972b:4,0x0f22c135:3,0xb0675803:1,0x9b3388fa:2,0x4676a268:10,0x3fb31dfc:.25,0xc0491d2e:200})
  self.nodes=self.rail('straight',1.2);self.put(P+0x1764,'<2I',*self.nodes[:2]);self.put(PHYSICS+0x22c,'<2I',self.nodes[0],RAIL)
  self.put(P+0x18,'<I',2);self.put(P+0x18cc,'<3f',.5,-60,0);self.put(P+0x18dc,'<f',0);self.put(P+0x71c,'<4f',0,0,8,1)
  self.put(P+0x24,'<4f',0,-60,0,1);self.put(OBJ+0x4c,'<4f',0,-60,0,1);self.put(OBJ+0xac,'<4f',0,0,0,1)
  self.put(INPUT+0x24c,'<f',amount);self.put(INPUT+0x250,'<2I',0,0)
  interpolation=self.alloc(0x40);self.put(CAM+0x90,'<I',interpolation);self.put(CAM+0xa0,'<I',P)
records=[]
def run(g,calls,label):
 frame_states.clear();completion_states.clear();commands.clear();speed_calls.clear()
 stages=g.run([call(0x417760,P+0x17b4),*calls],label,{0x7cce14:NET,0x7d1ec8:0,0x696d60:1000,0x684fc8:bits(6)})
 records.append({'label':label,'calls':len(stages),'frames':list(frame_states),'completion_states':list(completion_states),'callbacks':oracle.word(CBSTATE),'state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls)})
 if not (oracle.word(CONTROL+0x24)&0x10000):assert all(x['position']==x['owner_position'] for x in frame_states),label
 return stages
for angle,amount,contact,network in itertools.product([-1.57079637,0,1.57079637],[0,1],['none','dead','live'],[False,True]):
 g=HangUpdateGraph(angle,amount,network);g.contact(contact,.5);run(g,[call(0x52d4b0,P,[Q])]*6,f'complete hang common {angle}/{amount}/{contact}/{network}')
for up,present,moving,mutation in itertools.product([False,True],[False,True],[False,True],['observe','cancel']):
 g=HangUpdateGraph(0 if up else 3.14159274);actors=[]
 if present:actors.append(g.plane(0 if up else -100,moving=moving,half=1024,flags=0x40)[0])
 g.scripts(actors,mutation);g.finish_script();g.put(CHANNELS+0x18,'<f',6)
 calls=[call(0x52d4b0,P,[Q])]*2
 if up:calls +=[call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)]
 calls +=[call(0x52d4b0,P,[Q])]*4
 run(g,calls,f'hang exit continued {up}/{present}/{moving}/{mutation}')
 if up:assert len(completion_states)==1 and any(x['state']==4 for x in frame_states),(up,present,moving,mutation,completion_states)
for state,network,counter in itertools.product([0,1,3,4,5,0xffffffff],[False,True],[0,1]):
 if state==3:g=RailUpdateGraph(angle=0,network=network)
 else:g=AirUpdateGraph(height=20 if state==1 else 0,vertical=-40 if state==1 else 0,speed=0)
 g.put(P+0x18,'<I',state);g.put(P+0x710,'<I',counter);g.put(P+0x70c,'<B',int(bool(counter)));g.put(NET,'<I',4 if network else 0)
 g.plane(0,half=1024,flags=0x20);run(g,[call(0x52d4b0,P,[Q])]*3,f'all common states {state}/{network}/{counter}')
for state in [0,1,2,3,4,5,0xffffffff]:
 g=HangUpdateGraph();g.put(P+0x18,'<I',state);g.put(CONTROL+0x26,'<B',1);run(g,[call(0x52d4b0,P,[Q])],f'common state cancellation {state}')
scope='Candidate complete52d4b0 walking dispatcher now calls all five recovered movement states, preserves out-of-range fallthrough, and continues hanging, climb/drop, animation completion, ground and air frames with pose, events, speed, lighting and camera. Full engine startup and playable browser training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000],
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
finish('walk-complete-update',scope,{},extra)
report=json.loads((folder/'walk-complete-update-original.json').read_text());report['records']=records
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['instruction_coverage']={'0x52d4b0':{'covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not frame_hits[i.address]],'excluded':{}}}
report['completed_frames']=sum(len(x['frames']) for x in records)
(folder/'walk-complete-update-routines.json').write_text(json.dumps({'0x52d4b0':{'bytes':463,'instructions':len(code),'name':'thug_walk_update_draft'}},indent=2)+'\n')
(folder/'walk-complete-update-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
