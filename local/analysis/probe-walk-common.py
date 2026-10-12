"""Original common Walk pose, up-vector, offset and speed/event updates."""
from pathlib import Path
source=Path('local/analysis/probe-walk-animation.py').read_text().split('for direction,alias')[0]
exec(compile(source,'<preserved animation/Walk object graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x527be0,99,'thug_walk_decay_model_offset_draft',0,'void',False,False,True),
 (0x527420,231,'thug_walk_restore_up_draft',0,'void',False,False,True),
 (0x528400,191,'thug_walk_filter_speed_event_draft',1,'void',False,False,True),
 (0x529ce0,642,'thug_walk_write_owner_draft',0,'void',False,False,True),
 (0x529800,198,'thug_walk_rotate_owner_draft',0,'void',False,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for row in [(0x481640,'thug_animation_update_time',0,'void',False,False),(0x52ad10,'thug_walk_transition_frame_draft',0,'void',True,False)]:
 bind(*row)  # Both entry observers are already installed by the animation prefix.
class CommonGraph(AnimationGraph):
 def __init__(self):
  super().__init__();self.parameters(overrides={**required_parameters,0xb32c972b:4,0x0f22c135:3})
  self.put(P+0x58,'<4f',0,1,0,1);self.put(P+0x24,'<4f',3,4,5,1);self.put(P+0x34,'<4f',2,-7,4,1)
  self.put(P+0x44,'<f',3);self.put(P+0x704,'<f',4);self.put(P+0x18dc,'<f',-.5)
for state,offset,rate in itertools.product([0,1,2,3,4,0xffffffff],[-4,0,3],[0,.5,120]):
 g=CommonGraph();g.put(P+0x18,'<I',state);g.put(P+0x9c,'<f',offset);g.parameters(overrides={**required_parameters,0xb32c972b:rate})
 g.run([call(0x527be0,P)]*2,f'model offset/{state}/{offset}/{rate}')
for up,disabled,rate in itertools.product([(0,1,0,1),(.5,.9995,0,1),(.6,.8,0,1),(0,-1,0,1),(0,0,0,1)],[0,1],[0,.5,120]):
 g=CommonGraph();g.put(P+0x58,'<4f',*up);g.put(P+0x72c,'<f',disabled);g.parameters(overrides={**required_parameters,0x0f22c135:rate})
 g.run([call(0x527420,P)]*2,f'up recovery/{up}/{disabled}/{rate}')
for state,age,speeds,previous in itertools.product([0,1,4],[0,99,100,101],[(0,0),(0,2),(2,0),(2,3)],[0,0x1d537eff]):
 g=CommonGraph();g.put(P+0x18,'<I',state);g.put(P+0x1c,'<I',250-age);g.put(P+0x704,'<2f',*speeds);g.put(P+0x78,'<I',0xaf895b3f)
 g.run([call(0x528400,P,[previous])]*2,f'speed event/{state}/{age}/{speeds}/{previous:x}',{0x7d1ec8:0,0x696d60:250})
for state,vertical,up in itertools.product([0,1,2,3,4,0xffffffff],[-2,-1,-.6,0,.6,1,2],[(0,1,0,1),(.6,.8,0,1),(0,0,0,1)]):
 g=CommonGraph();g.put(P+0x18,'<I',state);g.put(P+0x744,'<f',vertical);g.put(P+0x58,'<4f',*up);g.put(P+0x48,'<4f',.6,0,.8,1)
 g.run([call(0x529ce0,P)]*2,f'write owner/{state}/{vertical}/{up}')
for timer,dt,angle,axis in itertools.product([0,.125,.5],[0,.125,.5],[-.7,.7],[(0,1,0,1),(.6,.8,0,0)]):
 g=CommonGraph();g.parameters(overrides={**required_parameters,0xb0675803:1});g.put(P+0x72c,'<2f',timer,angle);g.put(P+0x80,'<f',dt);g.put(P+0x734,'<4f',*axis)
 g.run([call(0x529ce0,P),call(0x529800,P),call(0x529800,P)],f'write/rotate owner/{timer}/{dt}/{angle}/{axis}')
# Connect actual advancing animation frames to the recovered pose-publication tail.
# Intermediate shared-frame collision/event helpers are still unfinished.
flow_records=[]
for direction,moving,tilted,timer in itertools.product([0,0xffffffff],[False,True],[False,True],[0,.5]):
 g=CommonGraph();g.parameters(overrides={**required_parameters,0xb32c972b:4,0x0f22c135:3,0xb0675803:1})
 g.put(CH+0x18,'<f',6 if direction else 2);g.put(CH+0x20,'<f',1);g.put(CH+0x24,'<I',direction)
 g.put(P+0x72c,'<2f',timer,.7);g.put(P+0x734,'<4f',0,1,0,1);g.put(P+0x80,'<f',.125)
 if not moving:g.put(GATE+0x18,'<I',0)
 else:g.put(PLATFORM+0x4c,'<4f',11,22,33,1)
 if tilted:g.put(P+0x58,'<4f',.6,.8,0,1)
 calls=[call(0x481640,CH),call(0x52ad10,P),call(0x527be0,P),call(0x527420,P),call(0x529ce0,P),call(0x529800,P),call(0x528400,P,[0])]*4
 g.run(calls,f'animation/common pose/{direction}/{moving}/{tilted}/{timer}')
 assert bytes(oracle.cpu.mem_read(OBJ+0x4c,16))==bytes(oracle.cpu.mem_read(P+0x24,16))
 assert oracle.word(P+0x18)==4
 flow_records.append({'direction':direction,'moving_contact':moving,'tilted':tilted,'timer':timer,'frames':4,'state':4,'owner_position_matches':True})
scope='Candidates for common Walk offset decay, up-vector recovery, speed/event filtering and publishing/rotating owner/model pose. All roots return; full common frame dispatch and original browser playability remain unfinished.'
saved=coverage.copy();coverage.clear();finish('walk-common',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-common-original.json').read_text());report['flow_records']=flow_records;report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
(folder/'walk-common-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-common-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
