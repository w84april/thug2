"""Complete particle simulation against original x86, with real game callees."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-particle-update.py').read_text().split('for mapping in ')[0],'<camera and ownership fixture setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for a,n,name,argc,result,heap,diag in [(0x49bb80,7,'particle_trail_segments',0,'word',False,False),(0x49bb50,18,'particle_trail_destroy',0,'void',True,True),(0x49bba0,33,'particle_trail_delete',1,'word',True,True),(0x4987f0,1934,'particle_update',2,'void',True,True)]:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag)
functions['0x4987f0']['float_args']=[0]
for a,name in [(0x497790,'particle_setup_script'),(0x497900,'particle_update_script')]:bind(a,'thug_'+name+'_draft',3,'void',True,True)
bind(0x461a00,'thug_object_manager_add',1,heap=True)
exports.extend([[0x64952c,'thug_particle_trail_methods_draft'],[0x649528,'thug_particle_trail_node_methods_draft'],[0x645c18,'thug_static_collision_methods']])
for name,address,value,width in [('thug_particle_time_scale_draft',0x700ef4,bits(60),4),('thug_collision_default_cache',0x691974,0,4),('thug_collision_select_farthest',0x691910,0,1)]:glob(name,address,value,width)
for j in range(1024):glob('thug_collision_fallback_indices',0x67c6b8+j*4,j*2|((j*2+1)<<16),offset=j*4)
initial=bytes(memory);oracle.initial=initial
class SimulationGraph(UpdateGraph):
 def __init__(self,count=3,segments=None):
  super().__init__();capacity=7;self.segments=1 if segments is None else segments
  self.put(P,'<I',0x64a5ac if segments is None else 0x64952c);fields.add(P)
  self.put(P+0x134,'<I',0 if segments is None else segments)
  self.records=self.alloc(48*(capacity+2))+48;self.positions=self.alloc(12*capacity*max(1,self.segments)+24)+12
  self.put(self.records-4,'<I',capacity);self.put(P+0xf8,'<I',self.records);self.put(P+0x11c,'<I',self.positions)
  self.put(P+0x7c,'<5I',capacity,0,bits(0),bits(0),count)
  self.put(P+0x90,'<16f',1,2,3,4,5,.3,.1,-.2,.3,1,2,3,4,1,.2,.7)
  self.put(P+0xd0,'<3f',.3,1,-.2);self.put(P+0xec,'<f',.25)
  self.put(P+0x12c,'<B',1);self.put(P+0x12f,'<B',1)
  for i in range(capacity):self.put(self.records+48*i,'<12f',1+i,2-i,3+i,.1,-.2,.3,1,2,3,4,i*.2,1)
  for i in range(capacity*max(1,self.segments)):self.put(self.positions+12*i,'<3f',1+i,-2-i,3+i)
  self.query=self.alloc(12);self.put(self.query,'<3I',0,0,0)
 def frame(self,dt=.016,paused=0):return call(0x4987f0,P,[bits(dt),paused,self.query])
def run_sim(g,calls,label,changes=None):
 try:result=case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
 if len(labels)%25==0:print('Original simulation',len(labels),flush=True)
 return result
for segments in [0,1,2,4,5,8,9]:
 for fn in [0x49bb50,0x49bba0]:
  for flag in [0,1,2,3]:
   g=SimulationGraph(segments=segments);run_sim(g,[call(0x49bb80,P),call(fn,P,[] if fn==0x49bb50 else [flag])],f'trail lifetime/{segments}/{fn:x}/{flag}')
for segments in [None,0,1,2,4,5,8,9]:
 for count in [0,1,3,7]:
  for dt in [0,.016,.7,-.1]:
   g=SimulationGraph(count,segments);run_sim(g,[g.frame(dt)]*3,f'integrate/{segments}/{count}/{dt}')
for paused in [0,1,255,256,257]:
 for enabled in [0,1]:
  g=SimulationGraph();g.put(P+0x12f,'<B',enabled);run_sim(g,[g.frame(paused=paused)],f'pause/{paused}/{enabled}')
for segments in [None,2]:
 for count in [0,1]:
  g=SimulationGraph(count,segments);g.put(P+0x125,'<B',1);run_sim(g,[g.frame()],f'disabled/{segments}/{count}')
for present in [False,True]:
 g=SimulationGraph();g.put(P+0x78,'<I',0x100)
 run_sim(g,([call(0x461a00,MANAGER,[OBJ])] if present else [])+[g.frame()],f'owner/{present}')
for segments in [0,1,5]:
 for count in [0,3,7]:
  for rate in [0,128]:
   g=SimulationGraph(count,segments);g.put(P+0x133,'<B',1);g.put(P+0x20,'<4f',0,0,100,1);g.put(P+0x70,'<f',rate)
   run_sim(g,[g.frame(.7)]*2,f'culled/{segments}/{count}/{rate}')
for players in [0,1,2]:
 for null in [False,True]:
  g=SimulationGraph();g.put(P+0x133,'<B',1)
  if null:g.put(P+0x600+24,'<I',0)
  run_sim(g,[g.frame()],f'viewports/{players}/{null}',{0x701378:players})
for rate in [0,1,128,-3]:
 for accumulator in [0,.003,.5]:
  for moving in [False,True]:
   g=SimulationGraph(1);g.put(P+0x70,'<2f',rate,accumulator);g.put(P+0x12c,'<B',moving)
   run_sim(g,[g.frame(.016)]*4,f'emission/{rate}/{accumulator}/{moving}')
for segments in [0,1,5]:
 for minimum in [0,1,3,7]:
  g=SimulationGraph(7,segments);g.put(P+0x80,'<I',minimum);g.put(P+0x84,'<2f',1,2)
  run_sim(g,[g.frame(.01)],f'distance removal/{segments}/{minimum}')
for setup in [False,True]:
 for update in [False,True]:
  g=SimulationGraph();g.programs();calls=[]
  if setup:calls.append(call(0x497790,P,[0xcd1e6836,0,0]))
  if update:calls.append(call(0x497900,P,[0x11223344,0,0]))
  run_sim(g,calls+[g.frame()]*3,f'retained scripts/{setup}/{update}')
source=Path('local/analysis/probe-particle-emission.py').read_text()
exec(compile('def triangle'+source.split('def triangle')[1].split('for small_faces in [')[0],'<verified real mesh builder>','exec'))
for present in [False,True]:
 for hit in [False,True]:
  g=SimulationGraph();actor,probe,vertices,points=triangle(g,False,False,False)
  geometry=g.word(actor+12);faces=g.word(geometry+12);g.put(faces+4,'<3H',0,2,1)
  radius=g.alloc(4);g.put(radius,'<B',255);g.put(actor+16,'<I',radius)
  cache=g.alloc(0xfd0);g.image[cache-BASE:cache-BASE+0xfd0]=bytes(0xfd0)
  g.put(cache,'<8f',-10000,-10000,-10000,1,10000,10000,10000,1)
  g.put(cache+32,'<2I',actor,geometry+16);g.put(cache+0xfc0,'<3I',int(present),int(present),0)
  g.put(P+0x20,'<4f',4 if hit else 50,40,4 if hit else 50,1);g.put(P+0x132,'<B',1)
  run_sim(g,[g.frame()],f'lighting/{present}/{hit}',{0x691974:cache})
  assert (oracle.word(P+0xec)!=bits(.25))==bool(present and hit)
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'Unreachable alignment skipped by unconditional branch.' for a in [0x49890a,0x498d98,0x498d9f,0x498e6d]}
scope='Complete4987f0 particle simulation and three actual trail-buffer virtual methods. Finite valid initialized point/trail graphs, zero/nonzero elapsed time, pause low byte, owner lookup and deletion, retained real setup/update scripts, emission accumulators, culling, offscreen expiry, integration, trail history, swap removal, distance reduction and real cached-triangle lighting. All arena/global/heap effects compare without numeric masks. Render methods and complete training frame remain unavailable; not playable.'
finish('particle-simulation',scope,excluded,extra)
