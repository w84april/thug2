"""Original Walk animation frames and real animation-time accessors."""
from pathlib import Path
source=Path('local/analysis/probe-walk-grab.py').read_text().split('for side,fraction,angle,kind')[0]
exec(compile(source,'<preserved initialized ground/contact graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x4813b0,58,'thug_animation_channel_times_draft',3,'void',False,False,True),
 (0x41a0e0,129,'thug_animation_component_times_draft',3,'void',False,False,True),
 (0x52ad10,550,'thug_walk_transition_frame_draft',0,'void',True,False,True),
 (0x5298d0,280,'thug_walk_finish_transition_draft',0,'void',True,True,True),
 (0x52a180,13,'thug_walk_finish_command_draft',2,'word',False,False,True)]
for row in specs:
 bind_new(*row);oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
for row in [(0x43ec40,'thug_walk_try_hang_draft',0,'byte',True,True),
 (0x441fc0,'thug_walk_try_rail_top_draft',0,'byte',True,False),
 (0x441de0,'thug_walk_try_rail_draft',1,'byte',True,False),
 (0x4738e0,'thug_script_initialize',0,'word',False,False),
 (0x474540,'thug_script_setup',4,'void',True,True),
 (0x4750b0,'thug_script_execute',0,'word',True,True),
 (0x481640,'thug_animation_update_time',0,'void',False,False),
 (0x4813f0,'thug_animation_timeline_finished',0,'byte',False,False)]:
 bind(*row)
 if row[0]!=0x43ec40:oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=row[0],end=row[0])
function_exports.append([0x52a180,'thug_walk_finish_command_draft'])
# Reuse literal parameter defaults required by all real grab/rail callbacks.
import ast
required_parameters={}
for filename,classname in [('probe-walk-transition.py','TransitionGraph'),('probe-walk-floor.py','FloorGraph'),('probe-walk-grab.py','GrabGraph')]:
 tree=ast.parse((folder/filename).read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==classname)
 constructor=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__')
 for node in ast.walk(constructor):
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='parameters':
   for keyword in node.keywords:
    if keyword.arg=='overrides':required_parameters.update(ast.literal_eval(keyword.value))
AP,AS,CH,OUT=P+0x13000,P+0x13100,P+0x13200,P+0x13400
SCRIPT=P+0x14000
class AnimationGraph(GrabGraph):
 def __init__(self,progress=.5,direction=0):
  super().__init__();self.parameters(overrides=required_parameters)
  self.image[AP-BASE:OUT-BASE+0x40]=bytes(OUT-AP+0x40)
  self.put(P+0x1774,'<I',AP);self.put(AP+0x34,'<I',AS);self.put(AS+4,'<I',1);self.put(AS+0x20,'<I',CH);self.put(CH+4,'<I',1)
  self.put(CH+0x14,'<3f',2,2+progress*4,6);self.put(CH+0x24,'<I',direction)
  self.put(P+0x18e4,'<4f',1,2,3,1);self.put(P+0x1904,'<4f',11,22,33,1)
  self.put(P+0x1914,'<2f',10,50);self.put(P+0x191c,'<4f',.6,0,.8,1);self.put(P+0x192c,'<2f',.75,.7)
  self.put(P+0x1934,'<4f',3,4,5,0);self.put(P+0x18,'<I',4)
for direction,alias in itertools.product([0,1,0xffffffff],['separate','same','current-start','start-direction','end-start']):
 g=AnimationGraph(direction=direction);args={'separate':[OUT,OUT+4,OUT+8],'same':[OUT]*3,'current-start':[CH+0x14,CH+0x18,OUT],
 'start-direction':[CH+0x24,CH+0x24,OUT],'end-start':[OUT,OUT+4,CH+0x14]}[alias]
 g.run([call(0x4813b0,CH,args)]*2,f'channel times/{direction}/{alias}')
for mode,direction,alias in itertools.product(['active','no channel','no state'],[0,1],['separate','same','component state']):
 g=AnimationGraph(direction=direction)
 if mode=='no channel':g.put(CH+4,'<I',0xffffffff)
 if mode=='no state':g.put(AS+4,'<I',0xffffffff)
 args={'separate':[OUT,OUT+4,OUT+8],'same':[OUT]*3,'component state':[AP+0x34,OUT+4,OUT+8]}[alias]
 g.run([call(0x41a0e0,AP,args)],f'component times/{mode}/{direction}/{alias}')
for kind,progress,direction in itertools.product(['absent','dead','still','translated','rotated Y','rotated X'],[0,.25,.5,1,1.5],[0,1]):
 g=AnimationGraph(progress,direction)
 if kind=='absent':g.put(GATE+0x18,'<I',0)
 if kind=='dead':g.put(CONTACT,'<I',0);g.put(PLATFORM+4,'<I',0)
 if kind=='translated':g.put(PLATFORM+0x4c,'<4f',11,22,33,1)
 if kind=='rotated Y':g.put(PLATFORM+0x6c,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,0,0,0,1)
 if kind=='rotated X':g.put(PLATFORM+0x6c,'<16f',1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1)
 g.run([call(0x52ad10,P)]*2,f'transition frame/{kind}/{progress}/{direction}')
# Final-pose commit without a callback, including non-axis-aligned facing.
for facing,delta in itertools.product([(0,0,1,1),(.6,0,.8,1),(-2,3,4,-1)],[(0,0,0,0),(10,-20,30,1)]):
 g=AnimationGraph();g.put(P+0x191c,'<4f',*facing);g.put(P+0x1934,'<4f',*delta)
 g.run([call(0x5298d0,P),call(0x52a180,P,[0,0])],f'finish pose/no callback/{facing}/{delta}')
# Member receiver adjustments use the real callbacks on a second live Walk object.
for callback,negative in itertools.product([0x4410c0,0x441190,0x43dcf0],[False,True]):
 g=AnimationGraph();nodes=g.rail_nodes(1);g.put(P+0x1764,'<I',nodes[0]);g.put(GATE+0x18,'<I',0)
 other=P+0x16000;g.image[other-BASE:other-BASE+0x1960]=g.image[P-BASE:P-BASE+0x1960]
 for offset in [0,0x1948]:fields.add(other+offset)
 root,receiver=(other,P) if negative else (P,other)
 g.put(root+0x1948,'<2I',callback,(receiver-root)&0xffffffff)
 g.run([call(0x5298d0,root)],f'finish receiver adjustment/{callback:x}/{negative}')
 assert oracle.word(receiver+0x18)==(2 if callback==0x43dcf0 else 3)
flow_records=[]
for kind,mode,progress in itertools.product(['hang','upper','rail'],['empty','script','advance','reverse'],[0,.5,1]):
 if mode in ['advance','reverse'] and progress!=0:continue
 g=AnimationGraph(progress);g.put(P+0x18,'<I',0);g.put(GATE+0x18,'<I',0);g.put(P+0x48,'<4f',0,0,1,1)
 if kind=='hang':
  nodes=g.rail();g.put(P+0x24,'<4f',0,-60,20,1);g.put(P+0x68,'<4f',0,-60,30,1);first=call(0x43ec40,P,[Q])
 else:
  nodes=g.rail_nodes(1,entering=kind=='rail');g.put(P+0x24,'<4f',0,0 if kind=='rail' else 100,0,1)
  first=call(0x441de0,P,[0,Q]) if kind=='rail' else call(0x441fc0,P,[Q])
 g.put(nodes[0]+0x4c,'<I',0x110)
 if mode!='empty':g.level_nodes([(0x110,[(0x2ca8a299,13,6)])]);g.callback([])
 # Original Walk vtable forwards extended descriptors through42bb20.
 g.put(OBJ+0x100,'<I',P);g.put(P+16,'<I',HANG)
 descriptor=g.alloc(24);g.put(descriptor,'<6I',0x9d3eebe8,0x726e85aa,0x52a180,0,0,0);fields.add(descriptor+8)
 g.symbol(0x9d3eebe8,9,descriptor);g.cached(0x77123456,b'\x01\x16'+struct.pack('<I',0x9d3eebe8)+b'\x01\x24')
 g.image[SCRIPT-BASE:SCRIPT-BASE+0x150]=bytes(0x150)
 frames=[call(0x52ad10,P)]
 if mode in ['advance','reverse']:
  g.put(CH+0x20,'<f',1);g.put(CH+0x18,'<f',6 if mode=='reverse' else 2);g.put(CH+0x24,'<I',0xffffffff if mode=='reverse' else 0)
  frames=[call(0x481640,CH),call(0x52ad10,P)]*4+[call(0x4813f0,CH)]
 steps=g.run([first,*frames,call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[0x77123456,0,0,OBJ]),call(0x4750b0,SCRIPT)],f'grab/frame/QB finish/{kind}/{mode}/{progress}')
 if mode in ['advance','reverse']:assert steps[-4]['result']==1
 assert steps[0]['result']==1 and oracle.word(P+0x18)==(2 if kind=='hang' else 3)
 flow_records.append({'kind':kind,'mode':mode,'progress':progress,'state':oracle.word(P+0x18),'callbacks':oracle.word(CBSTATE),'execute_result':steps[-1]['result']})
scope='Animation-time accessors, Walk animation frame, final-pose commit and its real QB member command. Connected grab/frame/interpreter sequences invoke hanging or rail callbacks through the stored member record. Timeline setup is initialized fixture data; the full animation scheduling, other walking states, startup and original browser playability remain unfinished.'
extra={**extra,'pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),'native_callbacks':[*extra.get('native_callbacks',[]),{'module':'walk-floor-diagnostics.wasm','export':'fixture_walk_floor_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
saved=coverage.copy();coverage.clear();finish('walk-animation',scope,{},extra);coverage.update(saved)
report=json.loads((folder/'walk-animation-original.json').read_text());report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
report['flow_records']=flow_records
(folder/'walk-animation-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
(folder/'walk-animation-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
