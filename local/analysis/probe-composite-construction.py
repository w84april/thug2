"""Original shared object builder, real physics initialization and lifetime."""
from pathlib import Path
exec(compile(Path('local/analysis/composite-construction-fixture-setup.py').read_text(),'<composite setup>','exec'))
specs=[(0x45e510,266,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45f2a0,46,'thug_component_create_registered_draft',1,'word',True,False),
 (0x45f3e0,60,'thug_component_track_draft',1,'void',False,False),
 (0x45f420,120,'thug_component_untrack_draft',1,'void',False,False),
 (0x45da30,83,'thug_composite_add_component_draft',1,'void',False,False),
 (0x45db30,83,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45ee20,267,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45da90,61,'thug_composite_add_array_draft',2,'void',True,True),
 (0x45dad0,91,'thug_composite_apply_node_draft',1,'void',True,False),
 (0x45f330,109,'thug_composite_create_draft',0,'word',True,False),
 (0x45f3a0,56,'thug_composite_create_from_array_draft',3,'word',True,True),
 (0x45d890,141,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45e620,33,'thug_composite_delete_draft',1,'word',True,True),
 (0x45d7c0,39,'thug_composite_defer_draft',0,'void',True,True),
 (0x45e500,14,'thug_composite_active_draft',0,'word',False,False)]
for row in specs:bind_new(*row)
bind(0x461a00,'thug_object_manager_add',1,heap=True)
bind(0x461ab0,'thug_dead_objects_flush_draft',0,heap=True,diag=True)
bind(0x500db0,'thug_physics_delete',1,'word',True)
bind(0x41d1d0,'thug_object_reference_assign',1)
PHYSICS=0x5bd63b29;NAME=0xa1dc81f9;TYPE=0xb6015ea8
def run(g,calls,label,changes=None):
    s=case(calls,g.patches(),changes,label)
    if len(labels)%25==0:print('Composite cases',len(labels),flush=True)
    return s
def init():return call(0x45e510,OBJ)
def pool(g,selected):
    g.put(POOL,'<6I',BLOCKS,BLOCKS+0x100,0,0,0,BLOCKS);g.put(POOL+0x58,'<I',0)
    for i in range(16):g.put(BLOCKS+i*16,'<I',BLOCKS+(i+1)*16 if i<15 else 0)
    return {0x6f3614:selected,0x6f361c+4*selected:POOL}
for fill in [0,0xa5,0xff]:
    g=CompositeGraph();g.image[OBJ-BASE:OBJ-BASE+0x108]=bytes([fill])*0x108
    run(g,[init(),init()],'constructor poison '+str(fill))
for flags in [0,1,2,3,0x100,0xfffffffe,0xffffffff]:
    g=CompositeGraph();g.put(OBJ+0x104,'<I',flags);run(g,[call(0x45e500,OBJ)],f'active bit {flags}')
# Factory selection takes the first duplicate type; the later invalid factory
# must never be called. A real factory allocates and constructs the component.
for types,target in [([],PHYSICS),([(7,0)],PHYSICS),([(PHYSICS,0x505440)],PHYSICS),([(7,0),(PHYSICS,0x505440),(PHYSICS,0)],PHYSICS)]:
    g=CompositeGraph();g.registry(types);calls=[call(0x45f2a0,MANAGER,[target])]
    if any(t==target for t,f in types):calls.append(call(0x500db0,HEAP,[1]))
    run(g,calls,'factory '+str(types))
for count in [0,1,4]:
    for match in [-1,0,count-1]:
        g=CompositeGraph();g.registry([(0x100+i,0) for i in range(count)])
        c=g.component(0x100+match if match>=0 else 0xdead);g.put(c+0x14,'<I',0xabcdef01)
        changes={0x6f0db8+4*i:g.component(0x100+i) for i in range(count)}
        run(g,[call(0x45f3e0,MANAGER,[c])],f'track count{count}/match{match}',changes)
for mode in ['empty','unknown','absent','head','middle','tail','later duplicate','first duplicate']:
    g=CompositeGraph();c=g.component();a=g.component();b=g.component();tail=g.component()
    g.registry([] if mode=='empty' else [(0x99 if mode=='unknown' else 0x12345678,0),(0x12345678,0)])
    g.put(a+0x14,'<I',b);g.put(b+0x14,'<I',0);g.put(c+0x14,'<I',tail)
    changes={0x6f0db8:a,0x6f0dbc:0}
    if mode in ['head','first duplicate']:changes[0x6f0db8]=c
    if mode=='first duplicate':changes[0x6f0dbc]=c
    if mode=='middle':g.put(a+0x14,'<I',c)
    if mode=='tail':g.put(b+0x14,'<I',c);g.put(c+0x14,'<I',0)
    if mode=='later duplicate':changes[0x6f0dbc]=c
    if mode=='unknown':g.registry([(0x99,0)])
    run(g,[call(0x45f420,MANAGER,[c])]*2,'untrack '+mode,changes)
for count in [0,1,3]:
    for linked in [False,True]:
        g=CompositeGraph();g.registry([(0x12345678,0)])
        comps=[g.component() for _ in range(count)];incoming=g.component();last=g.component()
        if linked:g.put(incoming+0x10,'<I',last)
        calls=[init()]+[call(0x45da30,OBJ,[c]) for c in comps]+[call(0x45da30,OBJ,[incoming]),call(0x45db30,OBJ),call(0x45d890,OBJ)]
        run(g,calls,f'append {count}/incoming next {linked}')
for registered,name,flag in itertools.product([False,True],[None,0,0x12345678,0xffffffff],[False,True]):
    g=CompositeGraph();v=g.vector([bits(12),bits(-3),bits(.25)]);q=g.vector([bits(.2),bits(-.3),bits(.4)])
    items=[(0x7f261953,6,v),(0xc97f3aa9,6,q)]+([(NAME,13,name)] if name is not None else [])+([(0,13,0x23627fd7)] if flag else [])
    node=g.structure(items);empty=g.structure([]);calls=[init()]
    if registered:calls += [call(0x461a00,MANAGER,[OBJ])]
    calls += [call(0x45dad0,OBJ,[node]),call(0x45dad0,OBJ,[empty]),call(0x45d890,OBJ)]
    run(g,calls,f'apply registered{registered}/name{name}/flag{flag}')
for n in [0,0x80000000,0xffffffff]:
    g=CompositeGraph();a=g.array(10,[]);g.put(a+4,'<I',n)
    run(g,[init(),call(0x45da90,OBJ,[a,0]),call(0x45db30,OBJ)],f'empty signed array {n}')
for flags in [0,1,2,255,256,257,0xffffffff]:
    g=CompositeGraph();run(g,[call(0x45f330,MANAGER),call(0x45e620,HEAP,[flags])],f'create real registration/delete {flags}')
# Real concrete component initialization, merge/cleanup, finalization and
# destruction. This is a synthetic generic owner exercising the shared builder,
# not the complete skater assembly or a training prop factory.
for overrides,pooled in itertools.product([False,True],[False,True]):
    g=CompositeGraph();g.registry([(PHYSICS,0x505440)]);g.symbol(0x78f80ec4,2,bits(.125))
    d=g.structure([(TYPE,13,PHYSICS),(0x100,1,4),(0x101,3,g.text('original')),(0x102,6,g.vector([bits(1),bits(2),bits(3)]))])
    o=g.structure([(0x100,1,9),(0x101,3,g.text('overridden')),(0x103,12,g.array(1,[10,20,30]))])
    changes=pool(g,1) if pooled else None
    run(g,[init(),call(0x45ee20,OBJ,[d,o if overrides else 0]),call(0x45db30,OBJ),call(0x45d890,OBJ)],f'parameters override{overrides}/pool{pooled}',changes)
for count,finalize in itertools.product([0,1,3],[0,1,255,256,257]):
    g=CompositeGraph();g.registry([(PHYSICS,0x505440)]);g.symbol(0x78f80ec4,2,bits(.125))
    descriptors=[g.structure([(TYPE,13,PHYSICS),(0x100,1,i)]) for i in range(count)]
    a=g.array(10,descriptors);node=g.structure([(NAME,13,0x12345678),(0x7f261953,6,g.vector([bits(1),bits(2),bits(3)]))])
    calls=[call(0x45f3a0,MANAGER,[a,node,finalize]),call(0x45d7c0,HEAP),call(0x461ab0,MANAGER)]
    run(g,calls,f'create from array{count}/finalize{finalize}')
exec(compile(Path('local/analysis/composite-construction-callback-setup.py').read_text(),'<explicit virtual witnesses>','exec'))
# These witnesses test dispatch order and live storage rules; the concrete
# physics paths above still execute only real game implementations.
for override in [False,True]:
    g,vt=witness_graph();c=g.component(methods=vt);g.put(CONTROL,'<I',c)
    d=g.structure([(TYPE,13,0x12345678),(0x100,1,1)]);o=g.structure([(0x100,1,2)])
    run(g,[init(),call(0x45ee20,OBJ,[d,o if override else 0]),call(0x45db30,OBJ),call(0x45d890,OBJ)],f'witness complete order overrides{override}')
for mode in ['no mutation','live next','reload head','moved live next']:
    g,vt=witness_graph();cs=[g.component(methods=vt) for _ in range(3)]
    if mode=='live next':mutate(g,3,0,(cs[0]+16,cs[2]))
    if mode=='reload head':mutate(g,3,0,(OBJ+0x100,cs[2]))
    if mode=='moved live next':mutate(g,4,3,(cs[0]+16,cs[2]))
    run(g,[init()]+[call(0x45da30,OBJ,[c]) for c in cs]+[call(0x45db30,OBJ)],'finalize witness '+mode)
for mode in ['ordinary','reload head','defer live next']:
    g,vt=witness_graph();cs=[g.component(methods=vt) for _ in range(3)]
    if mode=='reload head':mutate(g,6,0,(OBJ+0x100,cs[2]))
    if mode=='defer live next':mutate(g,5,0,(cs[0]+16,cs[2]))
    calls=[init(),call(0x461a00,MANAGER,[OBJ])]+[call(0x45da30,OBJ,[c]) for c in cs]
    calls += [call(0x45d7c0 if mode=='defer live next' else 0x45d890,OBJ)]
    run(g,calls,'lifetime witness '+mode)
for mode in ['single inline','ordinary','captured count and pointer','live entries','live method table']:
    g,vt=witness_graph();objectvt=g.alloc(44);alternatevt=g.alloc(44)
    g.put(objectvt+36,'<I',targets['add']);g.put(alternatevt+36,'<I',targets['add_alt']);fields.update([objectvt+36,alternatevt+36])
    g.put(OBJ,'<I',objectvt);descriptors=[g.structure([(0x100,1,i)]) for i in range(3)]
    a=g.array(10,descriptors[:1] if mode=='single inline' else descriptors);o=g.structure([])
    if mode=='captured count and pointer':mutate(g,7,0,(a+4,0),(a+8,0xdeadbeef))
    if mode=='live entries':mutate(g,7,0,(g.word(a+8)+4,descriptors[2]))
    if mode=='live method table':mutate(g,7,0,(OBJ,alternatevt))
    run(g,[call(0x45da90,OBJ,[a,o])],'array witness '+mode)
excluded={'0x45f363':'allocation failure is outside the successful live-object contract',
 '0x45ee9b':'original allocator is initialized',
 '0x45eeba':'allocation failure is outside the successful temporary structure contract',
 '0x45eee7':'null temporary cannot satisfy preceding merge/init contract'}
scope='Fifteen original composite construction/lifetime entrypoints. Real allocation, base construction, type metadata, manager registration/rename/removal, physics factory and initialization, script structure merge and cleanup, component finalization, deferred queue and destruction execute. Explicit test-only callback witnesses additionally observe ordering and mutation of live component links, reloaded heads/method tables, captured array count/storage and live descriptor entries. They do not implement game components. Full arena, registry globals, method identities, allocator route/order, preserved registers and return values compare. Generated synthetic objects exercise infrastructure, not training prop factories. Command virtual slots remain explicitly unavailable; no playable scene or renderer claimed.'
finish('composite-construction',scope,excluded,extra)
