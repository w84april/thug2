"""Original completed animation-state Walk frames, including speed/pose/camera."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-frame-speed.py').read_text().split('for mode,control,network,speed,previous')[0],'<walking speed parent graph>','exec'))
bind(0x52d4b0,'thug_walk_update_animation_prefix_draft',0,'void',True,True)
bind(0x481640,'thug_animation_update_time',0,'void',False,False)
for at in [0x52d4b0,0x481640]:oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=at,end=at)
oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=0x52d4b0,end=0x52d4b0)
frame_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:frame_hits.update([at]),begin=0x52d4b0,end=0x52d67e)
# Use the existing real critical-point diagnostic boundary inside this frame.
import ast
DLOG=P+0x20000
node=next(n for n in ast.parse((folder/'probe-walk-critical.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='critical_debug')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<preserved diagnostic boundary>','exec'));debug.__code__=critical_debug.__code__
extra={**extra,'native_callbacks':[*[x for x in extra.get('native_callbacks',[]) if DIAG+4 not in x.get('slots',[])],{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]}]}
CAM=P+0x18000
class FrameGraph(FrameSpeedGraph):
 def __init__(self,mode=3,direction=0,moving=False,counter=1,shape='empty',cancel=False):
  super().__init__(mode=mode,direction=direction,speed=30)
  self.parameters(overrides={**required_parameters,0x1a47ffab:2,0x0ab2db54:4,0xb32c972b:4,0x0f22c135:3,0xb0675803:1,0x9b3388fa:2,0x4676a268:10,0x3fb31dfc:.25})
  self.put(HANG+16,'<I',SCORECOMP);self.put(SCORECOMP+16,'<I',0);self.put(SCORE+0x14,'<i',-1)
  self.put(PHYSICS+0x150c,'<I',INPUT);self.put(INPUT+0xe0,'<B',0)
  self.put(P+0x18,'<I',4);self.put(P+0x710,'<i',counter);self.put(P+0x70c,'<B',1);self.put(P+0x9a,'<B',1);self.put(INPUT+0x100,'<B',0)
  self.put(CONTROL+0x26,'<B',int(cancel));self.put(P+0x1760,'<I',CAM);self.image[CAM-BASE:CAM-BASE+0x100]=bytes(0x100)
  self.put(P+0x58,'<4f',0,1,0,1);self.put(P+0x48,'<4f',0,0,1,1)
  self.put(CHANNELS+0x18,'<f',6 if direction else 2);self.put(P+0x71c,'<4f',0,0,0 if shape=='empty' else 8,1)
  self.put(DIAG,'<I',DLOG);self.image[DLOG-BASE:DLOG-BASE+16+32*192]=bytes(16+32*192)
  self.populated();self.put(AS+0x68,'<I',OBJ);self.put(PLAYER+0x14,'<I',OBJ);self.put(OBJ+0x14,'<I',0x1234);self.put(OBJ+0x2bc,'<I',0)
  self.put(EM+8,'<I',self.table([(0x1234,OBJ)]))
  if not moving:self.put(GATE+0x18,'<I',0)
  else:self.put(PLATFORM+0x4c,'<4f',11,22,33,1)
  if shape!='empty':self.obstacle('z',5,moving=shape=='moving wall')
flow_records=[]
for mode,direction,moving,pool in itertools.product([1,2,3],[0,0xffffffff],[False,True],[None,1]):
 g=FrameGraph(mode,direction,moving);changes={0x7cce14:NET}
 if pool is not None:changes.update({0x6f3614:pool,0x6f361c+4*pool:g.pool()})
 commands.clear();speed_calls.clear()
 g.run([call(0x481640,CHANNELS),call(0x52d4b0,P,[Q])]*4,f'complete animation Walk frames/{mode}/{direction}/{moving}/{pool}',changes)
 assert oracle.word(P+0x18)==4 and oracle.word(P+0x710)==0 and oracle.cpu.mem_read(P+0x70c,1)==b'\0'
 assert oracle.cpu.mem_read(OBJ+0x4c,16)==oracle.cpu.mem_read(P+0x24,16)
 assert oracle.cpu.mem_read(CAM+0x7c,16)==oracle.cpu.mem_read(P+0x48,16)
 assert len(commands)==len(speed_calls)==4 and all(x['return']==2 for x in commands)
 flow_records.append({'mode':mode,'direction':direction,'moving_contact':moving,'pool':pool,'frames':4,'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
for shape,cancel,counter in itertools.product(['empty','static wall','moving wall'],[False,True],[-1,0,1,3]):
 g=FrameGraph(shape=shape,cancel=cancel,counter=counter);commands.clear();speed_calls.clear()
 g.run([call(0x481640,CHANNELS),call(0x52d4b0,P,[Q])]*3,f'animation frame collision/cancel/counter/{shape}/{cancel}/{counter}',{0x7cce14:NET})
 assert oracle.word(P+0x18)==4 and len(speed_calls)==(0 if cancel else 3)
 assert oracle.word(P+0x710)==((counter if cancel else min(counter,0))&0xffffffff)
 flow_records.append({'shape':shape,'cancelled':cancel,'counter':counter,'frames':3,'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
scope='Complete original52d4b0 frame returns for animation state4, with actual input/owner reads, elapsed time, score decay, collision correction, pose/events, animation speed, camera and focus-input checks. Moving contact, selected pool, populated queues, cancellation and counters are exercised. Other states stop at explicit boundaries and the whole dispatcher is not claimed recovered; no playable level is claimed.'
extra={**extra,'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000]}
saved=coverage.copy();coverage.clear();finish('walk-frame-speed-flow',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-frame-speed-flow-original.json').read_text());report['flow_records']=flow_records
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['partial_frame']={'address':'0x52d4b0','covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not frame_hits[i.address]],'completed_state':4,'completed_calls':sum(x['frames'] for x in flow_records),'recovered_routine':False}
(folder/'walk-frame-speed-flow-original.json').write_text(json.dumps(report,indent=2)+'\n');print('CONNECTED',len(flow_records),'sequences',report['partial_frame'])
