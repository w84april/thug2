"""Bounded original channel allocation, fade state and live list creation."""
from pathlib import Path
source=Path('local/analysis/probe-camera-composite-startup-v3.py').read_text().split('\nfor fill,alignment,param')[0]
exec(compile(source,'<preserved initialized camera and skater oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x481ee0,56,'thug_animation_channel_allocate_v1',2,'word',True,False,False),(0x481990,12,'thug_animation_channel_is_fading_v1',0,'byte',False,False,True),(0x481b40,55,'thug_animation_channel_begin_fade_v1',1,'byte',False,False,True),(0x47de20,293,'thug_animation_state_begin_channel_v1',1,'void',True,False,True)]
for row in specs:bind_new(*row)
functions['0x481b40']['float_args']=[0];functions['0x47de20']['float_args']=[0]
for a,n in [(0x648794,'thug_animation_channel_methods'),(0x6486cc,'thug_animation_link_methods')]:
 if a not in {r[0] for r in exports}:exports.append([a,n])
global_default('thug_animation_channel_pool_index',0x6f92c8,0)
for i in range(2):
 a=0x6f92d0+4*i
 if a not in index:glob('thug_animation_channel_pools',a,0,offset=4*i)
 else:defaults[index[a]]=0
global_default('thug_animation_channel_limit_v1',0x6f8a68,4)
oracle.globals=globals_;oracle.defaults=defaults;initial=bytes(memory);oracle.initial=initial
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:fields.add(cpu.reg_read(UC_X86_REG_ECX)),begin=0x481830,end=0x481830)
class ChannelGraph(CameraCompositeGraph):
 def pool(self,capacity=8):
  pool=self.alloc(96);blocks=self.alloc(capacity*0x80 or 0x80);self.put(pool,'<6I',blocks,blocks+capacity*0x80,0,0,0,blocks if capacity else 0);self.put(pool+88,'<I',0)
  for i in range(capacity):self.put(blocks+i*0x80,'<I',blocks+(i+1)*0x80 if i+1<capacity else 0)
  return pool
 def state(self,count,statuses=None):
  state=self.alloc(0x74);sentinel=state+0x14;self.put(sentinel,'<5I',0,0xffffffff,0,sentinel,sentinel);self.put(state+0x68,'<I',OBJ)
  nodes=[self.alloc(0x74) for _ in range(count)]
  # The original traversal follows previous(+0c), starting at state+20.
  chain=[sentinel,*nodes,sentinel]
  for i,c in enumerate(nodes,1):
   self.put(c,'<5I',0x648794,c,0,chain[i+1],chain[i-1]);self.put(c+0x38,'<I',(statuses or [2]*count)[i-1]);self.put(c+0x54,'<I',0);self.put(c+0x5c,'<2f',.25,.5);self.put(c+0x64,'<3I',OBJ,0,0);self.put(c+0x70,'<B',1);fields.add(c)
  self.put(sentinel+12,'<2I',nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel)
  word=lambda a:int.from_bytes(self.image[a-BASE:a-BASE+4],'little')
  for c in [sentinel,*nodes]:assert word(word(c+12)+16)==c and word(word(c+16)+12)==c,(hex(c),'invalid caller channel list')
  return state
for selected,capacity,size in itertools.product([0,1],[0,1,4],[0,1,0x74,0x80]):
 g=ChannelGraph();pool=g.pool(capacity);g.run([call(0x481ee0,args=[size,0xffffffff])],f'channel selected pool/{selected}/{capacity}/{size}',{0x6f92c8:selected,0x6f92d0+4*selected:pool})
for size,failure in itertools.product([0,1,0x74,256],[False,True]):
 g=ChannelGraph();g.put(CONTEXT+32,'<I',int(failure));g.run([call(0x481ee0,args=[size,0x12345678])],f'channel generic heap/failure/{size}/{failure}')
for fill,alignment,status,duration in itertools.product([0,0xa5,255],[0,1,4],[0,1,2,3,0xffffffff],[0,.25,-.5]):
 g=ChannelGraph(fill);c=P+alignment;g.put(c+0x38,'<I',status)
 g.run([call(0x481990,c),call(0x481b40,c,[bits(duration)]),call(0x481990,c),call(0x481b40,c,[bits(duration)])],f'raw fade predicate/transition/{fill}/{alignment}/{status}/{duration}')
for count,limit,duration,pooled,status in itertools.product([0,1,2,4],[0,1,2,4],[0,.25],[False,True],[1,2]):
 g=ChannelGraph();state=g.state(count,[status if i%2==0 else 1 for i in range(count)]);changes={0x6f8a68:limit}
 if pooled:changes[0x6f92d0]=g.pool()
 g.run([call(0x47de20,state,[bits(duration)])]*2,f'original bounded channel list/create/fade/delete/{count}/{limit}/{duration}/{pooled}/{status}',changes)
scope='Four channel-creation dependencies for actual Animation startup. Real selected/empty pools and generic heap allocation/failure, poisoned unaligned status storage, boolean low-byte returns, repeated zero/positive/negative fade transitions, live initialized sentinel lists, max-channel removal with real destructor/free callees, PC24 finite fade accumulation and repeated channel creation compare. Initialized allocator, valid channel ownership/lists and successful internal root allocation required; only direct allocation wrapper failure is supported. No clip playback, full Animation419dd0/480410, profile startup, frame, rendered skater or gameplay credit. No fake game callee or numeric/checker changes.'
finish('animation-channel-startup-v3',scope,{'0x481efe':'initialized allocator contract excludes literal cold bootstrap call','0x47df29':'unchecked internal channel allocation failure faults before return; valid live storage contract'}, {**extra,'function_exports':function_exports})
(folder/'animation-channel-startup-v3-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
