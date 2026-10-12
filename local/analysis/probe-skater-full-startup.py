"""Complete actual original skater constructor; no game-callee substitution."""
from pathlib import Path
source=Path('local/analysis/probe-skater-final-startup.py').read_text().split('# Final complete startup cases.')[0]
exec(compile(source,'<verified final startup and texture setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
bind_new(0x582d90,1639,'thug_skater_construct_complete_draft',6,'word',True,True,True)
for a,name in [(0x64bef0,'thug_local_net_pending_methods_draft'),(0x64bdb8,'thug_end_run_methods_draft'),(0x64ba30,'thug_balance_component_pending_methods_draft'),(0x64ed24,'thug_balance_record_methods_draft'),(0x64bf38,'thug_looping_sound_pending_methods_draft')]:exports.append([a,name])
for a,name in [(0x513630,'thug_local_net_create_draft'),(0x510f90,'thug_end_run_create_draft'),(0x4f9170,'thug_balance_component_create_draft'),(0x513ad0,'thug_looping_sound_create_draft')]:function_exports.append([a,name])
registry=[(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280),(0xd8cc3428,0x4fbe20),(0x726e85aa,0x52a5c0),(0x7cd3e6d5,0x513630),(0xb1d5a3e1,0x510f90),(0x589e5fb3,0x4f9170),(0xb5f1e9d2,0x513ad0)]+[(int(c['type'],16),int(c['factory'],16)) for c in components]
local_chain=[0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58,0xd8cc3428,0x726e85aa,0x7cd3e6d5,0xb1d5a3e1,0x589e5fb3,0xb5f1e9d2,0x1859f772,0x4ff8dac6,0x408d2aa9,0x8bce7e66,0x380d909a]
remote_chain=[0x850eef66,0xd8cc3428,0x125044e2,0xb1d5a3e1,0xb5f1e9d2]

registry += [(0x5b512edc,0x51da80),(0xd1515392,0x4ecf20)]
records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,1,7,8,0xffffffff]):
 g=FinalGraph(difficulty=(len(records)%3),toggle=(len(records)%2));g.symbol(0x78f80ec4,2,bits(.125));g.registry(registry)
 mutate=bool(len(records)%2)
 if mutate:g.put(DLOG+4,'<3I',OBJ+0x14,0x77700000+len(records),2)
 pooled=len(records)%4 in [1,2];changes={0x690fa0:0xfffffffe}
 if pooled:
  pool=g.alloc(96);blocks=g.alloc(64*8);g.put(pool,'<6I',blocks,blocks+64*8,0,0,0,blocks);g.put(pool+88,'<I',0)
  for i in range(64):g.put(blocks+i*8,'<I',blocks+(i+1)*8 if i<63 else 0)
  changes.update({0x6f3614:1,0x6f3620:pool})
 args=[17,MANAGER,local,id_,heap_index,0x12345678];stages=g.run([call(0x582d90,OBJ,args)],f'complete original constructor/{heap_index}/{local}/{id_}',changes)
 assert stages[0]['result']==OBJ and not stages[0].get('expected_trap')
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+(local_chain if local&255 else remote_chain)+[0x18223fd6,0x488af07a,0x5b512edc,0xd1515392]
 links={t:c for c,t in chain};assert oracle.word(OBJ+0x27c)==links[0x18223fd6]
 assert oracle.word(OBJ+0x28c)==(links[0x4ff8dac6] if local&255 else 0)
 for offset,texture,w in [(0x1c,TEXTURES+0x20000,128),(0x20,TEXTURES+0x60000,64)]:
  wrapper=oracle.word(links[0x5b512edc]+offset);resource=oracle.word(wrapper+16);assert oracle.word(resource+16)==texture
  assert bytes(oracle.cpu.mem_read(texture+0x100,w*w*4))==bytes(oracle.cpu.mem_read(texture-0x20000+0x100,w*w*4))
 assert oracle.word(CONTEXT+28)==0 and oracle.word(CONTROL+4)==4
 records.append({'arguments':args,'components':chain,'returned_this':stages[0]['result'],'diagnostics_mutate_id':mutate,'structure_pool_selected':pooled,'temporary_scope_restored':True,'texture_copies_equal':True})
missing=[hex(i.address) for i in coverage[0x582d90] if not hits[i.address]];print('ROOT MISSING',missing,flush=True)
scope='Complete original582d90 local/remote skater constructor returnsTHIS and performs final descriptor/override cleanup after all real component factories and actual tag/sticker image cloning. Exact owner/heap/global/registry/diagnostic behavior and preserved registers compare over80 initialized original calls with pooled and generic structure storage. Bounded valid startup graphs and successful internal allocations; cold heap bootstrap and failure paths that fault before return are outside this scope. Component finalization, frames, main startup, rendering and a playable original level remain unfinished.'
# Explicit initialized allocator/unreachable branch exclusions are reviewed after discovery.
finish('skater-full-startup',scope,{**{a:'initialized allocator contract excludes cold process bootstrap' for a in ['0x582efb','0x58333d']},**{a:'unchecked descriptor/override allocation failure faults before return; valid storage contract' for a in ['0x582f28','0x58336a']}},extra)
f=folder/'skater-full-startup-original.json';j=json.loads(f.read_text());j['complete_constructor']={'address':'0x582d90','returned_calls':len(records),'records':records,'counted_complete':False,'pending_node_and_browser':True};j['assets']=assets;f.write_text(json.dumps(j,indent=2)+'\n')
