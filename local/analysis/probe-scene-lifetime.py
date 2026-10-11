from pathlib import Path
exec(compile(Path('local/analysis/scene-lifetime-fixture-setup.py').read_text(),'<lifetime fixture>','exec'))
bind_new(0x460930,16,'thug_object_delete_unless_deferred_draft',heap=True,diag=True)
bind_new(0x59fb10,21,'thug_scene_kill_object_draft',2,this=False)
bind_new(0x461b00,31,'thug_object_enqueue_dead_draft',1)
bind_new(0x461ab0,80,'thug_dead_objects_flush_draft',heap=True,diag=True)
bind_new(0x5b0a40,14,'thug_flush_dead_objects_draft',2,'byte',this=False)
bind_new(0x460a50,69,'thug_object_defer_delete_draft',heap=True,diag=True)
bind(0x461cc0,'thug_object_manager_visit_draft',2)
functions['0x461cc0']['pointer_args']=[0]
for flags in [*range(16),0x100,0x102,0x80000000,0xffffffff]:
 for registered in [False,True]:
    p=ready_object(flags=flags)
    calls=([call(0x461a00,MANAGER,[OBJ])] if registered else [])+[call(0x460930,OBJ)]
    case(calls,p,label=f'delete guard flags{flags:x},registered{registered}')
for match in [0,1]:
 for flags in [0,2,0x80000000,0xffffffff]:
    p=ready_object(flags=flags)+[patch(KILL_CONTEXT,'<2I',0x100 if match else 0x12345678,0xfefefefe)]
    case([call(0x461a00,MANAGER,[OBJ]),call(0x59fb10,args=[OBJ,KILL_CONTEXT])],p,label=f'kill callback match{match},flags{flags:x}')
for count in [0,1,3,7]:
 for flags in [0,2,0xffffffff]:
    p=sum((ready_object(i,flags) for i in range(count)),[])
    calls=[call(0x461b00,MANAGER,[OBJ+i*512]) for i in range(count)]+[call(0x461ab0,MANAGER)]*2
    case(calls,p,label=f'enqueue and flush real base destructors {count}/{flags:x}')
for null_at in [0,1,2]:
    p=sum((ready_object(i) for i in range(3)),[])+[patch(OBJ+null_at*512+0x2c,'<I',0)]
    case([call(0x461b00,MANAGER,[OBJ+i*512]) for i in range(3)]+[call(0x5b0a40,args=[0xdeadbeef,0xfefefefe])]*2,p,label='flush null queued value '+str(null_at))
# Deferred deletion unregisters immediately and clears secondary references;
# primary references and owned script storage remain until the actual flush.
for flags in [0,1,2,3,0x100,0xffffffff]:
 for have_script in [False,True]:
    p=ready_object(flags=flags)
    calls=[call(0x461a00,MANAGER,[OBJ]),call(0x41d1d0,REF,[OBJ]),call(0x41d1d0,REF+16,[OBJ+0x40])]
    if have_script:
        p += [raw(SCRIPTS,bytes(244)),patch(SCRIPTS+0x2c,'<I',SCRIPTS+0x1c),patch(SCRIPTS+0x94,'<I',SCRIPTS+0x34),patch(SCRIPTS+0xe8,'<I',0x12345678),patch(OBJ+0x10,'<I',SCRIPTS)]
        calls += [call(0x4738e0,SCRIPTS),call(0x41d1d0,SCRIPTS+0xbc,[OBJ])]
    calls += [call(0x460a50,OBJ),call(0x5b0a40,args=[0,0])]
    stages=case(calls,p,label=f'defer then real flush flags{flags:x},script{have_script}')
    assert oracle.word(REF)==0 and oracle.word(REF+16)==0
    if have_script:assert oracle.word(0x6f353c)==0
# Run the actual Kill callback through the newly recovered reentrant traversal.
# Destruction invokes real manager removal, which requests traversal restart.
for count in [1,3,7]:
 for mode in ['first','last','all','none','guarded']:
    p=sum((ready_object(i,2 if mode=='guarded' and i%2 else 0) for i in range(count)),[])
    for i in range(count):
        match=mode in ['all','guarded'] or (mode=='first' and i==0) or (mode=='last' and i==count-1)
        p.append(patch(OBJ+i*512+0x14,'<I',0x100 if match else 0x200+i))
    p.append(patch(KILL_CONTEXT,'<2I',0x100,0xfefefefe))
    calls=[call(0x461a00,MANAGER,[OBJ+i*512]) for i in range(count)]
    calls += [call(0x461cc0,MANAGER,[0x59fb10,KILL_CONTEXT])]
    case(calls,p,label=f'actual kill callback and traversal {count}/{mode}')
scope='Six complete original lifetime routines: guarded direct deletion, the real Kill-by-ID callback, dead-object enqueue, dead-list flush, native FlushDeadObjects and deferred deletion. Real base-object destructors, registry removal/restart, parameters, references and script cleanup execute. Sequences prove deferred objects unregister/clear secondary references first and release primary references/owned script storage at flush. Queued deletion ignores the direct-delete guard; null queued values only unlink. Actual reentrant traversal invokes Kill callbacks with real removals. Entire registry arena, scoped services, globals, heap order and preserved registers compare without substituted gameplay callbacks. This does not implement the complete scene Kill dispatcher or concrete skater destruction.'
finish('scene-lifetime',scope,extra=extra)
