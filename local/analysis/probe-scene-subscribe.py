from pathlib import Path
exec(compile(Path('local/analysis/scene-lifetime-oracle.py').read_text(),'<registry helper>','exec'))
bind_new(0x462620,143,'thug_script_listener_add_draft',1,heap=True)
bind_new(0x463370,213,'thug_script_subscribe_draft',2,heap=True)
bind_new(0x472fd0,51,'thug_script_set_event_wait_draft',1,heap=True)
bind(0x463450,'thug_script_unsubscribe',2,heap=True)
for key in [0,1,5,0x12345678,0xffffffff]:
 for selected in [0,1]:
  for pooled in [False,True]:
    p=[];changes={0x6f0fc8:selected}
    if pooled:
        p += [patch(POOL,'<6I',BLOCKS,BLOCKS+0x100,0,0,0,BLOCKS),patch(POOL+0x58,'<I',0),patch(BLOCKS,'<I',BLOCKS+32),patch(BLOCKS+32,'<I',0)]
        changes[0x6f0fd0+selected*4]=POOL
    calls=[call(0x463370,EM,[key,SCRIPTS]),call(0x463370,EM,[key,SCRIPTS]),call(0x463370,EM,[key,SCRIPTS+256]),
           call(0x463370,EM,[key^4,SCRIPTS]),call(0x463450,EM,[key,SCRIPTS]),call(0x463450,EM,[key,SCRIPTS+256])]
    case(calls,p,changes,f'subscribe dedup/collision/removal,key{key:x},pool{pooled}/{selected}')
for count in [0,1,3,7]:
 for value in [SCRIPTS,SCRIPTS+256,SCRIPTS+512]:
    list_=OWNED;p=[patch(list_,'<5I',0x6478dc,0xffffffff,0,list_+32 if count else list_,list_+32+(count-1)*32 if count else list_)]
    for i in range(count):
        node=list_+32+i*32;p.append(patch(node,'<5I',0x6478d8,SCRIPTS+(i%3)*256,0,node+32 if i+1<count else list_,node-32 if i else list_))
        fields.add(node)
    fields.add(list_)
    case([call(0x462620,list_,[value])]*2,p,label=f'listener direct append count{count},value{value:x}')
for key in [0,1,5,0xffffffff]:
 for flag in [0,1,0x10,0xff]:
    p=[raw(SCRIPTS,bytes(244)),patch(SCRIPTS+0xa4,'<3I',0x87654321,0x12345678,0xfefefefe),patch(SCRIPTS+0xcc,'<B',flag)]
    case([call(0x472fd0,SCRIPTS,[key])]*2,p,label=f'event wait{key:x},flags{flag:x}')
# Null-valued equal-key inline head does not suppress collision-chain lookup.
for null_head in [0,1]:
    list_=OWNED;node=OWNED+32;fields.update([list_,node])
    p=[patch(LISTENERS+32,'<3I',4,0 if null_head else list_,NODES),patch(NODES,'<3I',4,list_,0),
       patch(list_,'<5I',0x6478dc,0xffffffff,0,node,node),patch(node,'<5I',0x6478d8,SCRIPTS,0,list_,list_)]
    case([call(0x463370,EM,[4,SCRIPTS])],p,label='existing listener in inline/overflow with null head '+str(null_head))
excluded={'0x46268b':'failed allocation cannot satisfy the original live listener-node contract',
 '0x4633e1':'initialized original allocator skips lazy bootstrap',
 '0x463417':'failed sentinel allocation cannot satisfy the subsequent append contract'}
scope='Three original routines recover unique event-listener append, event subscription and event-wait setup. Actual table insert/remove, listener disposal, selected fixed-pool allocation, heap allocation and temporary scopes execute. Duplicate script identities, hash collisions, null-valued inline heads, selected pool index, real unsubscribe cleanup, zero event and all retained wait fields/flags compare over the complete initialized registry arena. Generic successful allocation and initialized allocator are contracts; failed-allocation and bootstrap instructions are excluded explicitly. No native gameplay or virtual callbacks are substituted.'
finish('scene-subscribe',scope,excluded)
