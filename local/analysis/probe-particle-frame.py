"""Particle frame prerequisites against original instructions and real scripts."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-particle-setup.py').read_text().split('for fn in [0x497790')[0],'<preserved particle setup services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result,heap,diag in [(0x433e90,4,'particle_suspend_far',0,'byte',False,False),
 (0x433ea0,172,'particle_suspend_ready',1,'byte',False,False),(0x496f60,62,'particle_advance_setup',0,'void',True,True),
 (0x497ab0,80,'particle_orientation',1,'word',False,False),(0x496970,56,'particle_position_get',5,'void',False,False),
 (0x4969b0,49,'particle_position_set',5,'void',False,False),(0x496c30,170,'particle_bounds',0,'void',False,False)]:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag)
bind(0x497790,'thug_particle_setup_script_draft',3,heap=True,diag=True)
bind(0x4739a0,'thug_script_set_object_wait',3,'void')
bind(0x4728f0,'thug_script_clear_wait',0,'void')
for name,at,value in [('thug_particle_suspend_half_counter_draft',0x6951b4,0),('thug_particle_suspend_quarter_counter_draft',0x6951b8,0),('thug_frame_length_scale',0x684fc8,bits(1))]:global_default(name,at,value)
initial=bytes(memory);oracle.initial=initial
class FrameGraph(SetupGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x138]=bytes(0x138)
  self.symbol(0xdb120fb5,2,bits(3));self.symbol(0x3271aa80,2,bits(7))
def run_frame(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original particle frame cases',len(labels),flush=True)
 return result
for distance in [-1.,0.,1.,9.,10.,49.,50.,100.,101.,1e30]:
 for force in [0,1,0xffffffff]:
  for out in [0,P+0x20,P+0x34]:
   g=FrameGraph();g.put(P+0x24,'<f',distance);g.put(P+0x34,'<f',10);g.put(P+0x44,'<I',force)
   g.put(P+0x30,'<B',force&255)
   run_frame(g,[call(0x433e90,P)]+[call(0x433ea0,P,[out])]*5,f'suspend/{distance}/{force}/{out}')
for counter in [0xfffffffe,0xffffffff]:
 g=FrameGraph();g.put(P+0x24,'<f',64);g.put(P+0x34,'<f',20)
 run_frame(g,[call(0x433ea0,P,[0])]*5,f'throttle-wrap/{counter}',{0x6951b4:counter,0x6951b8:counter})
for angles in [(0.,0.,0.),(.1,.2,.3),(-1.,2.,-3.),(1.5707963267948966,0.,0.)]:
 for out in [P+0x200,P+0xe0,P+0xd0]:
  g=FrameGraph();g.put(P+0xe0,'<3f',*angles);run_frame(g,[call(0x497ab0,P,[out])],f'orientation/{angles}/{out}')
for segment in range(3):
 for index_ in range(4):
  for alias in ['distinct','same','next-source']:
   g=FrameGraph();positions=g.alloc(4*3*12);g.put(P+0x7c,'<I',4);g.put(P+0x11c,'<I',positions)
   g.put(positions,'<36I',*[0x3f000000+i*12345 for i in range(36)])
   source=positions+(segment*4+index_)*12
   outs=[P+0x200,P+0x204,P+0x208] if alias=='distinct' else [P+0x200]*3 if alias=='same' else [source+4,source+8,source]
   run_frame(g,[call(0x496970,P,[index_,segment,*outs]),call(0x4969b0,P,[index_,segment,0x7f812345,0x80000000,0xffc12345]),call(0x496970,P,[index_,segment,*outs])],f'positions/{segment}/{index_}/{alias}')
for acceleration in [(0,0,0),(1,-2,3),(3,2,1),(-2,3,1),(1e30,-2e30,3e30)]:
 for extent in [(1,2,3),(3,2,1),(1,3,2),(-1,-2,-3)]:
  for life in [0.,.5,2.,-1.,1e20]:
   g=FrameGraph();g.put(P+0x20,'<4f',2,3,4,1);g.put(P+0xa8,'<3f',*acceleration)
   g.put(P+0x98,'<3f',*extent);g.put(P+0xcc,'<f',life);g.put(P+0x94,'<f',.25)
   run_frame(g,[call(0x496c30,P)]*2,f'bounds/{acceleration}/{extent}/{life}')
for owner in [0,OBJ]:
 for wait in [None,3,15]:
  g=FrameGraph();g.programs();args=g.structure([(0x711,1,5)])
  calls=[call(0x496f60,P),call(0x497790,P,[0xcd1e6836,args,owner])]
  if wait is not None:calls += [call(0x4739a0,HEAP,[wait,OBJ,0]),call(0x496f60,P),call(0x4728f0,HEAP)]
  calls += [call(0x496f60,P)]*2
  run_frame(g,calls,f'retained-setup/{owner}/{wait}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={}
scope='Seven complete particle update prerequisites: Suspend readiness and far flag, retained setup-script execution/cleanup, effect orientation, raw segmented position access and derived bounds. Real scripts execute, wait, resume and release owned state. Counters wrap and advance under forced readiness; output aliases, ordered maxima and finite wide-exponent PC24 arithmetic compare without masks. These are prerequisites for the full particle update; no full frame or playability claimed.'
finish('particle-frame',scope,excluded,extra)
