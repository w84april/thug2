"""Original state storage and channel events; no old builders or output writes."""
from pathlib import Path
source=Path('local/analysis/probe-camera-viewport-v1.py').read_text().split('for flags,shape in')[0]
exec(compile(source,'<preserved initialized original oracle setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x47f150,218,'thug_animation_state_construct_storage_v1',3,'word',True,False,True),
       (0x47ea80,26,'thug_animation_state_enable_channel_events_v1',1,'void',False,False,True)]
for row in specs:bind_new(*row)
# Owner and component are pointer parameters; the component is a registered
# caller identity and must use the frozen checker's declared relocation.
functions['0x47f150']['pointer_args']=[0,1]
exports.extend([[0x648714,'thug_animation_state_pending_methods_v1'],[0x648710,'thug_animation_state_links_pending_methods_v1']])
for fill,alignment,flag,script_present,waiting in itertools.product([0,0xa5,255],[0,1,4],[0,1,2,255,256,257,0xffffffff],[False,True],[0,1]):
 g=FinalGraph(fill);p=P+alignment;owner=g.alloc(0x20);script=g.alloc(0xf4) if script_present else 0
 g.put(owner+0x10,'<I',script);g.put(p+0x60,'<B',waiting)
 if script:g.put(script+0xa4,'<I',0xabcdef01)
 fields.update([p,p+0x14,p+0x68,p+0x6c])
 stages=g.run([call(0x47f150,p,[owner,Q,flag])]*2,f'Animation state repeated storage/{fill}/{alignment}/{flag}/{script_present}/{waiting}')
 assert stages[-1]['result']==p
 if script:assert oracle.word(script+0xa4)==(0 if waiting else 0xabcdef01)
 assert oracle.word(p+0x68)==owner and oracle.word(p+0x6c)==Q
for alignment,marker,flag,shape in itertools.product([0,1,4],[0,1,0xfffffffe,0xffffffff],[0,1,2,255,256,257,0xabcdef81],['distinct','self head','embedded sentinel']):
 g=FinalGraph(0xa5);p=P+alignment;head=g.alloc(0x80)+alignment if shape=='distinct' else p if shape=='self head' else p+0x14
 g.put(p+0x20,'<I',head);g.put(head+4,'<I',marker)
 # Aliasing the embedded sentinel's channel flag still executes original stores.
 g.run([call(0x47ea80,p,[flag])]*2,f'Animation channel event low byte/{alignment}/{marker}/{flag}/{shape}')
scope='Two Animation state dependencies: constructor storage with actual empty-gap-list clearing and original Script clear-wait callee, and channel-event flag propagation through a valid mapped nonnull head. Raw poisoned/unaligned bytes, low-byte flags, repeated construction, absent/present script payloads, conditional wait clearing, sentinel rejection and overlapping heads compare. Identity-only state/embedded tables do not establish virtual dispatch, configuration, animation clip or asset startup, full419dd0/profile initialization, rendering or gameplay. Generic initialized services and bounded valid storage required; no fake game callee, engine numeric allowance or comparator change.'
finish('animation-state-storage-v3',scope,{},extra)
(folder/'animation-state-storage-v3-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
