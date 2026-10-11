"""Original particle manager and heap constructors; no installer/native execution."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved component comparison services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
specs=[(0x5bc620,134,'heap_gap_construct',1,True),(0x5bc4e0,40,'heap_gap_attach',1,False),
 (0x5ba260,194,'heap_base_construct',3,False),(0x5ba520,52,'heap_construct',3,False),
 (0x5bb4e0,113,'heap_registry_create',3,True),(0x49af20,285,'particle_manager_construct',0,True)]
for a,n,name,argc,heap in specs:bind_new(a,n,'thug_'+name+'_draft',argc,'void' if a==0x5bc4e0 else 'word',heap)
engine_exports=[[0x658a5c,'thug_heap_gap_methods_draft'],[0x65845c,'thug_heap_base_methods_draft'],
 [0x658480,'thug_heap_sentinel_methods_draft'],[0x658458,'thug_heap_block_methods_draft'],[0x65848c,'thug_heap_methods_draft'],
 [0x6494b0,'thug_particle_manager_methods_draft'],[0x6494c4,'thug_particle_list_methods_draft'],[0x6494c8,'thug_particle_heap_name_draft']]
exports+=engine_exports
glob('thug_allocator_registry_draft',0x7d1800,ALLOCATOR);glob('thug_particle_time_scale_draft',0x700ef4,0xdeadbeef)
put(ALLOCATOR+0xc0,'<I',0)
initial=bytes(memory);oracle.initial=initial
extra['pointer_symbols']=[[0x6494c8,'thug_particle_heap_name_draft','FlxParticles']]
def check(g,calls,label):
 try:return case(calls,g.patches(),None,label)
 except Exception:print('FAILED',label,flush=True);raise
for fill in [0,0xa5,0xff]:
 for size in [0,1,15,16,17,31,32,0x5000,0x501f]:
  g=PropGraph();g.image[P-BASE:P-BASE+0x18]=bytes([fill])*0x18
  check(g,[call(0x5bc620,P,[size])]*2,f'gap/{fill}/{size}')
for mode in [0,1,2,3,4,0x7fffffff,0x80000000,0xffffffff]:
 for fill in [0,0xa5,0xff]:
  g=PropGraph();gap=g.alloc(24);name=g.text('heap-name');g.put(gap,'<6I',0xaabbccdd,0x100020,0xa5a5a5a5,0x200040,0x11223344,0x55667788)
  g.image[P-BASE:P-BASE+0x98]=bytes([fill])*0x98;g.put(P+0x28,'<I',mode)
  check(g,[call(0x5bc4e0,gap,[P]),call(0x5ba260,P,[gap,mode,name]),call(0x5ba520,P,[gap,mode,name])],f'heap/{mode:x}/{fill}')
for count in [0,1,45]:
 for mode in [1,2]:
  g=PropGraph();gap=g.alloc(24);name=g.text('registered');g.put(ALLOCATOR+0xc0,'<I',count)
  check(g,[call(0x5bc620,gap,[0x501f]),call(0x5bb4e0,ALLOCATOR,[gap,mode,name])]*2,f'registry/{count}/{mode}')
for size in [None,0,1,31,0x5001]:
 for rate in [None,(1,0),(2,0x80000000),(1,1),(1,60),(1,0xffffffff),(1,0x7fffffff),(1,0x80000000),(2,bits(.7)),(2,bits(-1.25)),(2,1),(2,0x7f7fffff),(2,0x7f800000),(2,0xff800000)]:
  g=PropGraph();g.image[P-BASE:P-BASE+0x28]=b'\xa5'*0x28
  if size is not None:g.symbol(0x91cb7552,1,size)
  if rate is not None:g.symbol(0x3214c818,*rate)
  check(g,[call(0x49af20,P)]*2,f'manager/{size}/{rate}')
scope='Six original constructors/attachment routines recover the particle manager, its dedicated raw heap gap, heap registration and embedded free-list metadata. Actual QB settings and PC24 time-scale arithmetic execute. Whole arena/globals/heap events compare; raw allocation remains the existing host port. Initialized process allocator, successful allocations, separate valid objects and registry capacity are explicit contracts. Virtual allocator/destructor methods, particle creation/update/rendering and playable frames remain unavailable.'
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]};print('MISSING',sorted(missing),flush=True)
excluded={'0x5bc660':'initialized process allocator; cold bootstrap is outside this routine contract',
 '0x5bb52e':'successful allocation contract; null allocation branch retained in C but unverified',
 '0x49af7c':'successful allocation contract; failed gap allocation cannot provide required live heap',
 '0x49afc6':'successful allocation contract; null list allocation branch retained in C but unverified'}
finish('particle-engine',scope,excluded,extra)
