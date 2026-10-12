"""Compare completed original ground-mode Walk frames without replacing callees."""
from pathlib import Path
import ast
exec(compile(Path('local/analysis/probe-walk-frame-speed.py').read_text().split('for mode,control,network,speed,previous')[0],'<preserved walking speed graph>','exec'))
# Reuse the original instruction-level retained-probe provenance unchanged.
source=(folder/'probe-walk-grounded.py').read_text()
exec(compile(source[source.index('# Retained probe identity'):source.index('for moving,height,flags')],'<preserved ground provenance>','exec'))
# The light graph adds its state after the existing animation and floor graph.
source=(folder/'probe-walk-ground-validation.py').read_text()
source=source[source.index('LIGHTLOW,'):source.index('\nrecords=[]')].replace('class ValidationGraph(TransferGraph):','class ValidationGraph(FrameSpeedGraph):')
exec(compile(source,'<ground light graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind(0x52d4b0,'thug_walk_update_ground_prefix_draft',0,'void',True,True)
oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=0x52d4b0,end=0x52d4b0)
oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=0x52d4b0,end=0x52d4b0)
frame_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:frame_hits.update([at]),begin=0x52d4b0,end=0x52d67e)
def frame_floor_root(cpu,at,size,user):
 global source_probe,copy_destination
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))!=oracle.stop:return
 if at==0x52d4b0:source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 else:
  root_records[-1]['indeterminate_words']=sorted(undefined_words)
  root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
for at in [0x52d4b0,0x52d67e]:oracle.cpu.hook_add(UC_HOOK_CODE,frame_floor_root,begin=at,end=at)
def frame_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0]
 file=bytes(cpu.mem_read(oracle.word(sp+8),32)).split(b'\0')[0];assert file==b'mponents\\WalkComponent.cpp'
 count=oracle.word(DLOG);assert count<32;oracle.setword(DLOG,count+1);row=bytearray(192);row[:len(fmt)]=fmt;row[64:64+len(file)]=file;row[188:192]=cpu.mem_read(sp+12,4)
 if fmt.startswith(b'D:'):
  assert fmt in [b'D:%s:%i: required_pos_adjustment = %g, %g, %g\n',b'D:%s:%i: m_critical_point_offset = %g, %g, %g\n'];row[96:120]=cpu.mem_read(sp+16,24)
 else:
  message=bytes(cpu.mem_read(oracle.word(sp+16),88)).split(b'\0')[0]
  assert fmt==b'M:%s:%i: %s\n' and message in [b'applying uber frig',b'adjusting position due to bad critical point',b'WALKING_GROUND, within moving object'];row[96:96+len(message)]=message
 cpu.mem_write(DLOG+16+192*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
debug.__code__=frame_debug.__code__
CAM=P+0x21000
class GroundFrameGraph(ValidationGraph,GroundedGraph):
 def __init__(self,local=True,speed=3,cancel=False):
  super().__init__(local=local,state=0)
  self.parameters(overrides={**required_parameters,0x1a47ffab:2,0x0ab2db54:4,0xb32c972b:4,0x0f22c135:3,0xb0675803:1,0x9b3388fa:2,0x4676a268:10,0x3fb31dfc:.25,0xc0491d2e:200})
  self.put(CONTROL+0x24,'<B',0);self.put(CONTROL+0x26,'<B',int(cancel));self.put(GATE+0x18,'<I',0)
  self.put(P+0x714,'<f',0);self.put(P+0x710,'<i',3);self.put(P+0x70c,'<B',1);self.put(P+0x58,'<4f',0,1,0,1);self.put(P+0x48,'<4f',0,0,1,1)
  self.put(P+0x24,'<4f',0,0,0,1);self.put(OBJ+0x4c,'<4f',0,0,0,1);self.put(OBJ+0xac,'<4f',0,0,speed,0);self.put(P+0x1794,'<4f',0,1,0,1)
  self.put(SHADOW+16,'<I',SCORECOMP);self.put(SCORECOMP+16,'<I',0);self.put(SCORE+0x14,'<i',-1)
  self.put(PHYSICS+0x150c,'<I',INPUT);self.put(INPUT+0xe0,'<B',0);self.put(INPUT+0xc0,'<B',0);self.put(INPUT+0x120,'<B',0)
  self.put(P+0x9a,'<B',1);self.put(INPUT+0x100,'<B',0)
  self.put(P+0x1760,'<I',CAM);self.image[CAM-BASE:CAM-BASE+0x100]=bytes(0x100)
  self.populated();self.put(NET,'<I',0);self.put(AS+0x68,'<I',OBJ);self.put(PLAYER+0x14,'<I',OBJ);self.put(OBJ+0x14,'<I',0x1234);self.put(OBJ+0x2bc,'<I',0)
  self.put(EM+8,'<I',self.table([(0x1234,OBJ)]))

records=[]
for moving,local,speed in itertools.product([False,True],[False,True],[0,3]):
 g=GroundFrameGraph(local,speed);g.plane(0,moving=moving,half=128,flags=0x20);commands.clear();speed_calls.clear()
 g.run([call(0x52d4b0,P,[Q])]*3,f'complete ground frames/{moving}/{local}/{speed}',{0x7cce14:NET,0x7d1ec8:1000})
 assert oracle.word(P+0x18)==0 and oracle.word(P+0x710)==0
 assert oracle.cpu.mem_read(OBJ+0x4c,16)==oracle.cpu.mem_read(P+0x24,16)
 records.append({'moving':moving,'local_light':local,'speed':speed,'frames':3,'final_state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
 print('ground sequence',len(records),'complete',flush=True)
for moving,shape,angle,running,network in itertools.product([False,True],['flat','wall','step'],[0,.7],[False,True],[False,True]):
 g=GroundFrameGraph();g.plane(0,moving=moving,half=128,flags=0x20)
 g.put(CAMERA+0x6c,'<16f',-1,0,0,0,0,1,0,0,0,0,-1,0,0,0,0,1)
 g.put(P+0x70c,'<B',0);g.put(P+0x710,'<I',0);g.put(INPUT+0x24c,'<f',1);g.put(INPUT+0x248,'<f',angle);g.put(INPUT+0x1c0,'<B',int(running));g.put(NET,'<I',4 if network else 0)
 if shape=='wall':g.obstacle('z',2,moving=moving)
 elif shape=='step':g.plane(1,moving=moving,half=128,flags=0x20)
 commands.clear();speed_calls.clear()
 g.run([call(0x52d4b0,P,[Q])]*4,f'active ground input/{moving}/{shape}/{angle}/{running}/{network}',{0x7cce14:NET,0x7d1ec8:1000})
 position=list(struct.unpack('<4f',oracle.cpu.mem_read(P+0x24,16)))
 assert oracle.word(P+0x18)==0 and oracle.cpu.mem_read(OBJ+0x4c,16)==oracle.cpu.mem_read(P+0x24,16)
 assert any(x['speed_bits'] for x in speed_calls),(moving,shape,angle,running,network,speed_calls)
 if shape!='wall':assert position[:3]!=[0,0,0]
 records.append({'moving':moving,'shape':shape,'angle':angle,'running':running,'network':network,'frames':4,'final_state':0,'position':position,'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
for moving,mutation in itertools.product([False,True],['observe','cancel','position','velocity']):
 g=GroundFrameGraph();actor,owner=g.plane(0,moving=moving,half=128,flags=0x40)
 g.trigger(mutation,g.word(actor+4));g.put(INPUT+0x24c,'<f',1);g.put(P+0x70c,'<B',0)
 if moving:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 commands.clear();speed_calls.clear()
 g.run([call(0x52d4b0,P,[Q])],f'complete ground callback/{moving}/{mutation}',{0x7cce14:NET,0x7d1ec8:1000})
 assert oracle.word(CBSTATE)>0
 records.append({'moving':moving,'mutation':mutation,'frames':1,'callbacks':oracle.word(CBSTATE),'final_state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
for cancel,shape in itertools.product([False,True],['empty','floor','moving ceiling']):
 g=GroundFrameGraph(cancel=cancel)
 if shape!='empty':g.plane(0,moving=False,half=128)
 if shape=='moving ceiling':g.plane(40,moving=True,velocity=(3,4,0,0))
 commands.clear();speed_calls.clear()
 g.run([call(0x52d4b0,P,[Q])],f'ground cancellation/fallback/{cancel}/{shape}',{0x7cce14:NET,0x7d1ec8:1000})
 records.append({'cancelled':cancel,'shape':shape,'frames':1,'final_state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
node=next(n for n in ast.parse((folder/'probe-walk-transfer.py').read_text()).body if isinstance(n,ast.ClassDef) and n.name=='TransferGraph')
ramp=next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name=='ramp');ramp.name='transfer_ramp'
exec(compile(ast.Module(body=[ramp],type_ignores=[]),'<preserved accepted ramp geometry>','exec'))
for moving,speed,age in itertools.product([False,True],[20,100],[500,501,1000]):
 g=GroundFrameGraph(speed=speed);g.plane(100,moving=False,half=16);transfer_ramp(g,moving)
 g.put(OBJ+0x4c,'<4f',0,100,0,1);g.put(P+0x24,'<4f',0,100,0,1);g.put(CAMERA+0x94,'<f',-1);g.put(P+0x1c,'<I',1000-age)
 mode=g.alloc(0x120);g.image[mode-BASE:mode-BASE+0x120]=bytes(0x120);g.put(mode+0x1c,'<I',1)
 g.put(GATE+0x2c,'<I',mode);g.put(PHYSICS+0x1534,'<I',P);g.put(OBJ+0x100,'<I',P);g.put(P+16,'<I',SHADOW)
 g.put(INPUT+0xc0,'<B',1);g.put(INPUT+0x120,'<B',1);g.put(INPUT+0x24c,'<f',1);g.put(INPUT+0x1c0,'<B',1);g.put(P+0x70c,'<B',0)
 g.symbol(0x8cbc89dd,10,g.structure([(0xfaa40754,2,bits(-800)),(0x95a79c32,2,bits(150))]))
 for key,value in [(0xc31ca696,1),(0x441c38a0,1),(0xbe33a41e,0),(0xe50a9d56,500),(0x32c20f7e,0)]:g.symbol(key,2,bits(value))
 g.symbol(0x9c8c6df1,1,0);commands.clear();speed_calls.clear()
 g.run([call(0x52d4b0,P,[Q])],f'complete transfer frame/{moving}/{speed}/{age}',{0x7cce14:NET,0x7d1ec8:1000})
 assert oracle.word(P+0x18)==int(speed==100 and age>500)
 records.append({'moving_transfer':moving,'speed':speed,'age':age,'frames':1,'final_state':oracle.word(P+0x18),'commands':list(commands),'speed_calls':list(speed_calls),'diagnostics':oracle.word(DLOG)})
scope='Complete original52d4b0 ground-mode frames with actual ground collision, validation, local/global light, shadow, pose/event, animation speed and camera. Air/hang/rail entry handlers remain explicit boundaries; no whole dispatcher or playable level is claimed.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],
 'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000],
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
finish('walk-ground-frame',scope,{},extra)
report=json.loads((folder/'walk-ground-frame-original.json').read_text());report['records']=records
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['partial_frame']={'address':'0x52d4b0','covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not frame_hits[i.address]],'completed_calls':sum(x['frames'] for x in records),'recovered_routine':False}
(folder/'walk-ground-frame-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['partial_frame'])
