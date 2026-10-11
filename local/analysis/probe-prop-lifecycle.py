"""Original prop factories, initialization and disposal with real shared callees."""
from pathlib import Path
exec(compile(Path('local/analysis/composite-construction-fixture-setup.py').read_text(),'<preserved composite setup>','exec'))
# Match the original selected SSE matrix dispatch used by the maintained
# Motion orientation oracle; this is engine startup state, not a game stub.
oracle.setword(0x684fe4,0x5df4ac)
names=[(0x433f50,124,'suspend_construct',0,'word',False,True),(0x434000,447,'suspend_initialize',1,'void',False,True),
 (0x4341c0,21,'suspend_finalize',0,'void',False,True),(0x433e50,8,'suspend_update',0,'void',False,True),
 (0x433e10,11,'suspend_destroy',0,'void',False,True),(0x433fd0,33,'suspend_delete',1,'word',True,True),(0x434290,86,'suspend_create',0,'word',True,False),
 (0x423d00,521,'motion_reset',0,'void',False,True),(0x424aa0,62,'motion_construct',0,'word',False,True),(0x426650,146,'motion_create',0,'word',True,False),
 (0x426720,66,'motion_initialize',1,'void',False,True),(0x424ae0,161,'motion_destroy',0,'void',True,True),(0x4266f0,33,'motion_delete',1,'word',True,True),
 (0x4ec370,25,'object_proximity_construct',0,'word',False,True),(0x4ec420,87,'object_proximity_create',0,'word',True,False),
 (0x4ec240,11,'object_proximity_destroy',0,'void',False,True),(0x4ec390,33,'object_proximity_delete',1,'word',True,True),
 (0x46ab90,33,'proximity_find',1,'word',False,False),(0x432d90,92,'object_sound_construct',0,'word',False,True),
 (0x433100,89,'object_sound_create',0,'word',True,False),(0x432ca0,51,'object_sound_initialize',1,'void',False,True),
 (0x47ad80,131,'sound_find_voice',1,'word',False,True),(0x47c7a0,27,'audio_stop_slot',1,'void',False,False),
 (0x47bb50,222,'sound_remove_owner',1,'void',False,True),(0x432df0,86,'object_sound_destroy',0,'void',False,True),
 (0x433160,33,'object_sound_delete',1,'word',True,True),(0x41f500,32,'lockobj_construct',0,'word',False,True),
 (0x41ff20,97,'lockobj_create',0,'word',True,False),(0x41f400,11,'lockobj_destroy',0,'void',False,True),(0x41f440,33,'lockobj_delete',1,'word',True,True),
 (0x41aad0,78,'component_b87c8e43_construct',0,'word',False,True),(0x41adc0,86,'component_b87c8e43_create',0,'word',True,False),
 (0x41a810,11,'component_b87c8e43_destroy',0,'void',False,True),(0x41a880,33,'component_b87c8e43_delete',1,'word',True,True),
 (0x51b970,8,'component_suspend_update',0,'void',False,True)]
for a,n,name,argc,result,heap,this in names:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
bind(0x45da30,'thug_composite_add_component_draft',1)
bind(0x45ee20,'thug_composite_add_parameters_draft',2,heap=True,diag=True)
bind(0x45d890,'thug_composite_destroy_draft',0,heap=True,diag=True)
bind(0x45db30,'thug_composite_finalize_draft',0,heap=True,diag=True)
bind(0x45f3a0,'thug_composite_create_from_array_draft',3,'word',True,True)
bind(0x45d730,'thug_component_construct',0,'word')
classes=[('suspend',0xce0ca665,0x4c,0x6465c8,0x433f50,0x434290,0x433e10,0x433fd0),
 ('motion',0x0a015e17,0x24c,0x64620c,0x424aa0,0x426650,0x424ae0,0x4266f0),
 ('object_proximity',0x1d5b1ae6,0x30,0x64b6c4,0x4ec370,0x4ec420,0x4ec240,0x4ec390),
 ('object_sound',0x07713c7b,0xc0,0x646514,0x432d90,0x433100,0x432df0,0x433160),
 ('lockobj',0x5cb5cb7e,0x90,0x6460e4,0x41f500,0x41ff20,0x41f400,0x41f440),
 ('component_b87c8e43',0xb87c8e43,0x4c,0x645dc4,0x41aad0,0x41adc0,0x41a810,0x41a880)]
for name,kind,size,vt,ctor,factory,destroy,delete in classes:
    table='thug_'+('object_proximity' if name=='object_proximity' else name)+'_methods_draft'
    exports.append([vt,table]);function_exports.append([factory,'thug_'+name+'_create_draft'])
    oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=ctor,end=ctor)
for name,at,value in [('thug_sound_device',0x7d6a38,1),('thug_sound_mode',0x7cefa8,0),('thug_sound_configuration',0x6f85a8,0),
 ('thug_sound_pending',0x6f85b0,0),('thug_sound_pending_count_draft',0x6f85bc,0)]:global_default(name,at,value)
for off in range(0,48*60,4):glob('thug_sound_voices',0x6f7a68+off,0,offset=off)
for off in range(0,48*24,4):glob('thug_audio_slots',0x6f85c8+off,0,offset=off)
P=BASE+0x1a0000
class PropGraph(CompositeGraph):
    def __init__(self,default=bits(50),forced=0):
        super().__init__();self.symbol(0xad501995,2,default);self.symbol(0x95edc6f6,1,forced)
        self.symbol(0xd3d072f9,2,bits(.75));self.symbol(0x0432f2a1,2,bits(1.25))
    def prox(self,keys):
        manager=self.alloc(8);nodes=[self.alloc(0xa8) for _ in keys];self.put(manager,'<2I',nodes[0] if nodes else 0,0)
        for i,k in enumerate(keys):self.put(nodes[i],'<I',k);self.put(nodes[i]+0xa4,'<I',nodes[i+1] if i+1<len(nodes) else 0)
        return manager,nodes
def run(g,calls,label,changes=None,floats=()):
    try:stages=case(calls,g.patches(),changes,label)
    except Exception:
        print('Failed prop case:',label,flush=True);raise
    for s in stages:s['float_fields']=list(floats)
    if len(labels)%40==0:print('Prop lifecycle cases',len(labels),flush=True)
    return stages
# Constructor/reset fields are compared over the complete poisoned arena.
for name,kind,size,vt,ctor,factory,destroy,delete in classes:
    for fill in [0,0xa5,0xff]:
        g=PropGraph();g.image[P-BASE:P-BASE+size]=bytes([fill])*size
        run(g,[call(ctor,P)]*2,name+' constructor poison '+str(fill))
    for flags in [0,1,2,3,255,256,257,0xffffffff]:
        g=PropGraph();run(g,[call(factory),call(delete,HEAP,[flags])],name+' factory/delete '+str(flags))
    g=PropGraph();g.image[P-BASE:P-BASE+size]=bytes(size)
    run(g,[call(ctor,P),call(destroy,P)],name+' direct destroy')
for fill in [0,0xa5,0xff]:
    g=PropGraph();g.image[P-BASE:P-BASE+0x24c]=bytes([fill])*0x24c
    run(g,[call(0x423d00,P)]*2,'motion reset poison '+str(fill))
for bits_ in [0,0x80000000,1,0x80000001,0x007fffff,0x00800000,bits(.125),bits(-25),bits(1e30),0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
    g=PropGraph(default=bits_);run(g,[call(0x433f50,P)],f'suspend wide product {bits_:x}',floats=[P+0x1c,P+0x20])
# Optional suspend distance, fallback ordering, forced distances and flags.
for distance,fallback,flag,forced in itertools.product([None,0,bits(2.5)],[None,bits(5)],[False,True],[0,1]):
    g=PropGraph(forced=forced);items=[]
    if distance is not None:items.append((0xe4279ba2,2,distance))
    if fallback is not None:items.append((0x4eedfae7,2,fallback))
    if flag:items.append((0,13,0xcb839dc1))
    s=g.structure(items)
    run(g,[call(0x433f50,P),call(0x434000,P,[s])]*2,f'suspend init {distance}/{fallback}/{flag}/{forced}')
for values in [(100,20,10,5),(-5,-5,-5,-5),(1e30,2e30,3e30,3e30)]:
    g=PropGraph();s=g.structure([(key,2,bits(v)) for key,v in zip([0x4eedfae7,0xd7e4ab5d,0xa0e39bcb,0x3e870e68],values)])
    run(g,[call(0x433f50,P),call(0x434000,P,[s])],f'suspend distance ordering {values}')
for word_ in [0x80000000,1,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xff812345]:
    g=PropGraph();s=g.structure([(key,2,word_) for key in [0xe4279ba2,0x4eedfae7,0xd7e4ab5d,0xa0e39bcb,0x3e870e68]])
    run(g,[call(0x433f50,P),call(0x434000,P,[s])],f'suspend float boundaries {word_:x}',floats=[P+o for o in [0x1c,0x20,0x34,0x38,0x3c,0x40]])
for found,flags in itertools.product([False,True],[0,1,2,0xfffffffe,0xffffffff]):
    g=PropGraph();g.put(P+12,'<I',OBJ);c=g.component(0x286a8d26 if found else 1)
    g.put(OBJ+0x100,'<I',c);g.put(P+8,'<I',flags)
    run(g,[call(0x4341c0,P),call(0x433e50,P)]*2,f'suspend finalize {found}/flags{flags}')
for ctor in [0x41aad0,0x433f50]:
    g=PropGraph();run(g,[call(ctor,P),call(0x51b970,P)]*2,f'virtual suspend through {ctor:x}')
for mode in ['missing','direct','included','wrong']:
    for angles in [None,(0,0,0),(.2,-.3,.4)]:
        g=PropGraph();items=[] if mode=='missing' else [(0xa1dc81f9,1 if mode=='wrong' else 13,0x12345678)]
        if angles is not None:items.append((0x9d2d0915,6,g.vector([bits(v) for v in angles])))
        s=g.structure(items)
        if mode=='included':g.symbol(0x34561234,10,s);s=g.structure([(0,13,0x34561234)])
        g.put(P+12,'<I',OBJ)
        run(g,[call(0x45e510,OBJ),call(0x424aa0,P),call(0x426720,P,[s])],f'motion node {mode}/{angles}')
# All combinations of Motion-owned child/buffers use the real base-component
# virtual destructor for the child, and real release order for both buffers.
for mask in range(8):
    g=PropGraph();g.image[P-BASE:P-BASE+0x24c]=bytes(0x24c);child=g.component();a=g.alloc(32);b=g.alloc(32)
    g.put(P+0x1ec,'<I',child if mask&1 else 0);g.put(P+0x1cc,'<I',a if mask&2 else 0);g.put(P+0x1f0,'<I',b if mask&4 else 0)
    run(g,[call(0x424ae0,P)],f'motion owned storage {mask}')
for keys,key in [([],0),([1],1),([1,2,1],1),([1,2,1],2),([1,2],3)]:
    g=PropGraph();manager,nodes=g.prox(keys);s=g.structure([(0x08470f2e,13,key)]);empty=g.structure([])
    run(g,[call(0x46ab90,args=[key]),call(0x432d90,P),call(0x432ca0,P,[s]),call(0x432ca0,P,[empty])],f'proximity lookup {keys}/{key}',{0x6f2268:manager})
# Shared builder integration invokes the actual factories/initializers for all
# four real descriptor types. Sound moved/update is explicitly unavailable, so
# this sequence stops before finalize and then executes real full destruction.
for extra_components in [False,True]:
    g=PropGraph();selected=classes[:4];g.registry([(kind,factory) for name,kind,size,vt,ctor,factory,destroy,delete in selected])
    a=g.array(10,[g.structure([(0xb6015ea8,13,kind)]) for name,kind,*rest in selected]);node=g.structure([(0xa1dc81f9,13,0x12345678)])
    calls=[call(0x45f3a0,MANAGER,[a,node,0])]
    if extra_components:
        for name,kind,size,vt,ctor,factory,destroy,delete in classes[4:]:
            c=g.alloc(size);g.image[c-BASE:c-BASE+size]=bytes(size);calls += [call(ctor,c),call(0x45da30,HEAP,[c])]
    calls.append(call(0x45d890,HEAP));run(g,calls,'four prop descriptor factories + extras '+str(extra_components))

# Add audio ownership/COM boundary cases below before finalizing this corpus.
exec(compile(Path('local/analysis/prop-lifecycle-audio-probes.py').read_text(),'<audio ownership checks>','exec'))
excluded={hex(a):'allocation-failure epilogue outside initialized successful-allocation fixture contract'
 for a in [0x4342d5,0x4342d9,0x4342db,0x4342e2,0x4342e5,
 0x4266cf,0x4266d3,0x4266d4,0x4266d6,0x4266d7,0x4266de,0x4266e1,
 0x433148,0x43314c,0x43314e,0x433155,0x433158,
 0x41ae05,0x41ae09,0x41ae0b,0x41ae12,0x41ae15]}
scope='Thirty-five original routines recover six prop component factories/constructors/destructors, Motion reset and node initialization, Suspend initialization/finalization/update, Sound proximity initialization and actual pending-owner/voice cleanup. Shared builder executes real factories and initializers for the four descriptor types and destroys them. Sound moved/update and other explicit zero virtual slots remain unavailable; no completed prop assembly or scene rendering is claimed. Full arena, globals, heap effects, preserved registers and returns compare. Only typed arithmetic Suspend outputs permit NaN classification; all other words are exact. Initialized services and successful heap allocations are explicit contracts. Audio stop uses a platform-boundary observation callback, not fabricated game behavior.'
finish('prop-lifecycle',scope,excluded,extra)
