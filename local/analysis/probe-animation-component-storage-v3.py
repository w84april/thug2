"""Original initialized-heap Animation component storage; no prior outputs rerun."""
from pathlib import Path
source=Path('local/analysis/probe-camera-viewport-v1.py').read_text().split('for flags,shape in')[0]
exec(compile(source,'<preserved viewport oracle setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x41a410,162,'thug_animation_component_construct_storage_v1',0,'word',True,False,True),
 (0x41a5b0,86,'thug_animation_component_create_storage_v1',0,'word',True,False,False)]
for row in specs:bind_new(*row)
exports.extend([[0x645d8c,'thug_animation_component_pending_methods_v1'],[0x645d88,'thug_animation_component_embedded_pending_methods_v1']])
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=FinalGraph(fill);fields.update([P+alignment,P+alignment+0x28]);g.run([call(0x41a410,P+alignment)]*2,f'animation component raw repeated storage/{fill}/{alignment}')
for fill,repeats in itertools.product([0,0xa5,255],[1,2,3]):
 g=FinalGraph(fill);g.run([call(0x41a5b0)]*repeats,f'animation component factory/{fill}/{repeats}')
for fill in [0,0xa5,255]:
 g=FinalGraph(fill);g.put(CONTEXT+32,'<I',1);g.run([call(0x41a410,P)],f'animation sentinel allocation failure/{fill}')
 g=FinalGraph(fill);g.put(CONTEXT+32,'<I',1);g.run([call(0x41a5b0)],f'animation outer allocation failure/{fill}')
missing={hex(i.address) for c in coverage.values() for i in c if not hits[i.address]};print('Missing',sorted(missing),flush=True)
scope='Animation component constructor and factory storage with initialized generic allocator. Real base construction, embedded intrusive-list identity, successful/null sentinel allocations, outer allocation failure, raw poisoned and unaligned gaps and repeated construction compare. Component and embedded vtables are identity-only; no virtual lifecycle, Animation QB initialization, cold allocator bootstrap, full profile startup or gameplay is claimed. No fake game callee, numeric allowance or checker change.'
excluded={'0x41a472':'initialized allocator contract excludes the reviewed cold-bootstrap call4e1950'}
assert missing==set(excluded),missing
finish('animation-component-storage-v3',scope,excluded,extra)
(folder/'animation-component-storage-v3-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
