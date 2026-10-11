from pathlib import Path
exec(compile(Path('local/analysis/scene-lifetime-fixture-setup.py').read_text(),'<lifetime fixture>','exec'))
bind_new(0x46abc0,232,'thug_proximity_set_active_draft',1,heap=True,diag=True)
bind_new(0x46acb0,50,'thug_proximity_set_named_draft',2,heap=True,diag=True,this=False)
bind(0x5b0a40,'thug_flush_dead_objects_draft',2,'byte',this=False)
P0,P1,P2,PM=BASE+0x15000,BASE+0x15100,BASE+0x15200,BASE+0x15300
glob('thug_proximity_manager_draft',0x6f2268,PM)
for at in [0x461480,0x460a50,0x472fd0,0x4619f0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
# A real cached, terminating QB program: newline/end-script. Spawn still runs
# constructor, setup, owner references and the actual bytecode executor.
program=[patch(CACHETABLE+8,'<I',1),patch(CACHETABLE+32+12,'<3I',5,CACHE+128,0),
         patch(CACHE+128,'<5I',5,CACHE+192,1,0,0),raw(CACHE+192,b'\x01\x24')]
def node(at,name,active,base,mask,next_=0):
    return [raw(at,bytes([0xad])*0xa8),patch(at,'<I',name),patch(at+0x54,'<B',active),
      patch(at+0x58,'<4I',base,mask,mask,0xabcdef01),patch(at+0xa0,'<2I',5,next_)]
def setup(active,base,mask,owners=True):
    p=node(P0,0x12345678,active,base,mask)+[patch(PM,'<IBBH',P0,0x75,0x96,0x1234)]+program
    calls=[]
    if owners:
      for i,key in enumerate([0,1,7,31] if not base else [(base+j)&0xffffffff for j in [0,1,7,31]]):
        if key==0xffffffff:continue # manager automatically renames this sentinel
        p+=ready_object(i)+[patch(OBJ+i*512+0x14,'<I',key)]
        calls.append(call(0x461a00,MANAGER,[OBJ+i*512]))
    return p,calls
for base in [0,0x100]:
 for active in [0,1,2,255]:
  for request in [0,1,2,255,256,257,0xffffffff]:
    p,calls=setup(active,base,0x80000083)
    calls += [call(0x46abc0,P0,[request]),call(0x5b0a40,args=[0,0])]
    case(calls,p,label=f'active{active},request{request:x},objectbase{base:x}')
for base in [0,0x100,0xfffffff0]:
 for mask in [0,1,2,4,0x80,0x80000000,0xffffffff,0x55555555]:
  for owners in [False,True]:
    p,calls=setup(1,base,mask,owners)
    calls += [call(0x46abc0,P0,[0]),call(0x5b0a40,args=[0,0])]
    case(calls,p,label=f'consume mask{mask:x},base{base:x},owners{owners}')
for mask in [0,1,0xffffffff]:
    p,calls=setup(1,0,mask)
    case(calls+[call(0x46abc0,P0,[0])],p,{0x6f2268:0},'missing proximity manager preserves mask '+hex(mask))
for request in [0,1,256,0xffffffff]:
 for lookup in ['null manager','empty','missing','first','second','duplicate']:
    p,calls=setup(1,0,0)
    p += node(P0,0x12345678 if lookup in ['first','duplicate'] else 0xabcdef01,1,0,0,P1)
    p += node(P1,0x12345678 if lookup in ['second','duplicate'] else 0xabcdef02,1,0,0)
    if lookup=='empty':p += [patch(PM,'<I',0)]
    changes={0x6f2268:0} if lookup=='null manager' else None
    case([call(0x46acb0,args=[0x12345678,request])],p,changes,f'name lookup{lookup},request{request:x}')
scope='Two complete original proximity-state routines. Direct active compares low bytes; named lookup normalizes the full word, chooses first matching linked node and tolerates missing managers/names. Active exit consumes live32-bit masks, including bit31 and wraparound object IDs. Real object lookup, deferred deletion, unregister/enqueue/destructor flush, and real script spawn/constructor/cache/owner-binding/bytecode execution run. The script branch executes a valid cached newline/end-script QB body; no spawn or deletion callback is replaced. Missing owners still change proximity dispatch flags; missing proximity manager leaves script mask untouched. Whole registry arena, spawned instances/references, globals and heap effects compare. Initialized registry/cache/services and successful allocations are contracts; production proximity-node loading and complete training scene dispatch remain.'
finish('scene-proximity',scope,extra=extra)
