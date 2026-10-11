"""Original movement helpers and the recovered subset of the Motion frame."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0],'<preserved prop services>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result,heap,diag in [
 (0x4258b0,185,'motion_rotate_axis',2,'void',False,False),
 (0x425a80,486,'motion_rotate_step',1,'byte',False,False),
 (0x425c70,64,'motion_rotate_axes',0,'void',False,False),
 (0x424440,116,'motion_interpolate',0,'void',False,False),
 (0x423740,140,'motion_bob',0,'void',False,False),
 (0x424200,567,'motion_translate',0,'byte',True,True),
 (0x4270e0,484,'motion_frame_prefix',0,'void',True,True)]:
 bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag)
functions['0x4258b0']['float_args']=[1]
bind(0x405990,'thug_matrix_interpolation_initialize',2)
for name,at,value in [('thug_frame_counter',0x7d1ec8,60),('thug_frame_rate',0x684fd0,bits(60)),
 ('thug_frame_length_scale',0x684fc8,bits(1)),('thug_timer_origin',0x696d64,0),
 ('thug_timer_offset',0x696d60,0),('thug_time_scale',0x67d7c0,bits(1)),
 ('thug_matrix_small_angle',0x67c648,0x3d0efa35)]:global_default(name,at,value)
initial=bytes(memory);oracle.initial=initial
IDENTITY=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
class MotionGraph(PropGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x24c]=bytes(0x24c)
  self.put(P+12,'<I',OBJ);self.put(OBJ+0x4c,'<4f',2,3,4,1)
  self.put(OBJ+0x6c,'<16f',*IDENTITY);self.put(OBJ+0xc0,'<16f',*([7.]*16))
  self.put(P+0x1e0,'<f',.125);self.put(P+0x1dc,'<I',1000);self.put(P+0x1d8,'<f',2.5)
  self.put(P+0x1d0,'<f',3.)
 def axis(self,axis=0,speed=1,target_speed=2,accel=0,brake=0,angle=1,accum=0,unlimited=False):
  for off,val in [(0x15c,speed),(0x14c,target_speed),(0x16c,accel),(0x17c,brake),(0x12c,angle),(0x13c,accum)]:self.put(P+off+4*axis,'<f',val)
  if unlimited:self.put(P+0x1c,'<I',self.word(P+0x1c)|(0x20<<axis))
 def linear(self,speed=2,accel=0,limit=4,distance=10,progress=0,dt=.125):
  self.put(P+0x108,'<4f',10,-6,14,2);self.put(P+0x18c,'<4f',2,3,4,1)
  for off,val in [(0x20,speed),(0x124,accel),(0x120,limit),(0x118,distance),(0x11c,progress),(0x1e0,dt)]:self.put(P+off,'<f',val)
 def interpolation(self,angle=0):
  import math
  a=self.alloc(64);b=self.alloc(64);state=self.alloc(152)
  target=IDENTITY[:];target[0]=target[10]=math.cos(angle);target[2]=-math.sin(angle);target[8]=math.sin(angle);target[12:15]=[7.,8.,9.]
  self.put(a,'<16f',*IDENTITY);self.put(b,'<16f',*target);self.put(P+0x1cc,'<I',state)
  return call(0x405990,state,[a,b])
 def arrival(self,kind):
  key=0x71449955;_,nodes=self.nodes([(key,0,[])])
  items=[(0xa1dc81f9,13,key)];entries=[]
  for prop,script in [(0x3aefe377,0x71664441),(0x86125749,0x71664442)]:
   if kind=='both' or kind==('spawn' if prop==0x3aefe377 else 'replace'):
    items.append((prop,13,script));program=self.alloc(16);self.image[program-BASE:program-BASE+2]=b'\x01\x24'
    entry=self.alloc(20);self.put(entry,'<5I',script,program,0,0,0);entries.append((script,entry))
  items.append((0x7031f10c,10,self.structure([(0x123,1,7)])))
  replacement=self.structure(items);self.put(nodes[0]+4,'<I',self.word(replacement+4));self.put(CACHE+20,'<I',self.table(entries));self.put(P+0x128,'<I',key)
def run_motion(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original motion cases',len(labels),flush=True)
 return result
# Repeated rotations use the real SSE multiply and orthogonalization routines.
for axis in [0,1,2,3,0xffffffff]:
 for angle in [0.,-0.,.125,-.5,1.5707963267948966,-3.,10.,-100.]:
  g=MotionGraph();run_motion(g,[call(0x4258b0,P,[axis,bits(angle)])]*3,f'axis/{axis}/{angle}')
axis_cases=[(1,2,0,0,1,0,False),(1,2,20,0,1,0,False),(-1,-2,-20,0,-1,0,False),
 (1,-2,20,0,1,0,False),(-1,2,-20,0,-1,0,False),(0,0,0,0,0,0,False),
 (1,0,0,16,1,0,False),(2,1,0,16,1,0,False),(-2,-1,0,-16,-1,0,False),
 (2,1,0,2,1,0,False),(-2,-1,0,-2,-1,0,False),(2,1,0,8,1,0,False),
 (2,2,0,0,.2,0,False),(-2,-2,0,0,-.2,0,False),(1,2,0,0,1,1,False),
 (1,2,0,0,1,0,True),(-1,-2,0,0,-1,0,True)]
for axis in range(3):
 for i,values in enumerate(axis_cases):
  g=MotionGraph();g.axis(axis,*values);run_motion(g,[call(0x425a80,P,[axis])]*3,f'axis-step/{axis}/{i}')
for flags in range(8):
 g=MotionGraph();g.put(P+0x18,'<I',flags|0x80000000)
 for axis in range(3):g.axis(axis,speed=axis+1,angle=.125)
 run_motion(g,[call(0x425c70,P)]*3,f'axis-flags/{flags}')
for duration,elapsed,dt in [(0,0,.125),(1,0,.125),(1,.875,.125),(1,1,.125),(-1,0,.125),(1,0,-.125),(1,.25,0)]:
 for angle in [0.,.5,2.]:
  g=MotionGraph();init=g.interpolation(angle);g.put(P+0x18,'<I',0xa5);g.put(P+0x1c4,'<2f',duration,elapsed);g.put(P+0x1e0,'<f',dt)
  run_motion(g,[init]+[call(0x424440,P)]*3,f'interpolation/{duration}/{elapsed}/{dt}/{angle}')
for period,counter,offset,origin in [(1000,0,0,0),(1000,15,0,0),(1000,30,0,0),(1000,45,0,0),(1000,60,0,0),
 (7,123,9,17),(1,0xffffffff,0xffffffff,1),(0x7fffffff,1,0x60000000,0),(0x80000001,1,0x70000000,0),(0xffffffff,1,0xffffffff,0)]:
 for amplitude in [0.,2.5,-3.]:
  g=MotionGraph();g.put(P+0x1dc,'<I',period);g.put(P+0x1d8,'<f',amplitude)
  run_motion(g,[call(0x423740,P)]*2,f'bob/{period}/{counter}/{offset}/{amplitude}',{0x7d1ec8:counter,0x696d60:offset,0x696d64:origin})
for values in [(2,0,4,10,0,.125),(2,1,4,10,0,.125),(2,5,4,10,0,.125),(-2,-1,4,10,0,.125),
 (2,0,4,10,9.75,.125),(2,0,4,10,11,.125),(0,0,4,0,0,.125),(0,0,4,10,0,.125),
 (3.25,.15,4.5,13.5,.3,.1),(1e20,0,1e20,1e25,1e15,.125)]:
 for scale in [.5,1.,2.]:
  g=MotionGraph();g.linear(*values);run_motion(g,[call(0x424200,P)]*3,f'translation/{values}/{scale}',{0x684fc8:bits(scale)})
for kind in ['none','spawn','replace','both']:
 g=MotionGraph();g.linear(progress=10);g.arrival(kind);run_motion(g,[call(0x424200,P)]*2,f'arrival/{kind}')
# Frame coverage is explicitly partial: path/rail/ballistic modes are excluded.
for remaining,velocity in [(0,4),(-0.,-4),(.01,0),(-.01,0),(10,0),(-10,0),(10,-5),(-10,5),(10,5),(-10,-5)]:
 for owner_id in [0,15,16,0xffffffff]:
  g=MotionGraph();g.put(P+0x19c,'<2f',velocity,remaining);g.put(OBJ+0x14,'<I',owner_id)
  run_motion(g,[call(0x4270e0,P,[0])]*4,f'frame-vertical/{remaining}/{velocity}/{owner_id}')
for flags in [1,7,8,0x20,0x80,0xaf,0x228]:
 g=MotionGraph();g.linear(distance=.08);g.put(P+0x18,'<I',flags)
 for axis in range(3):g.axis(axis,angle=.02)
 init=g.interpolation(.5);g.put(P+0x1c4,'<f',.03)
 # 0x228 demonstrates translation precedence without entering missing rail;
 # only one call is valid once the completed translation clears its own bit.
 run_motion(g,[init]+[call(0x4270e0,P,[0])]*(1 if flags==0x228 else 4),f'frame-modes/{flags}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={'0x425c79':'unreachable alignment instruction'}
for a in ['0x427168','0x42716a','0x42716f','0x427176','0x427178','0x427185','0x427187','0x42718c','0x42718f','0x427195','0x427198','0x42719a','0x4271a0','0x4271a3','0x4271a9','0x4271ac','0x4271b2']:excluded[a]='partial frame only; path, rail and ballistic modes remain unavailable and explicitly trap in Wasm'
scope='Six complete Motion helper control flows: bob, translation, interpolation, axis rotation, axis stepping and axis loop. Finite inputs, valid axes for axis stepping, nonzero bob period and nonzero translation timestep. Actual matrix, timing and node-arrival script callees. Complete arena, globals, returns, registers and heap effects compare exactly. Frame4270e0 is PARTIAL: only these helpers, vertical movement and orientation copy; path, rail and ballistic modes remain explicit unavailable boundaries. No completed gameplay frame or playability claimed.'
finish('motion-frame',scope,excluded,{**extra,'partial_functions':['0x4270e0']})
