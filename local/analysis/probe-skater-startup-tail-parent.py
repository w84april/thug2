"""Both original skater branches interrupted before tag/sticker initialization."""
from pathlib import Path
source=Path('local/analysis/probe-skater-startup-tail.py').read_text().split('# Complete-function behavioral cases.')[0]
exec(compile(source,'<verified original component test setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
bind(0x582d90,'thug_skater_construct_startup_tail_prefix_draft',6,'void',True,True)
for a,name in [(0x64bef0,'thug_local_net_pending_methods_draft'),(0x64bdb8,'thug_end_run_methods_draft'),(0x64ba30,'thug_balance_component_pending_methods_draft'),(0x64ed24,'thug_balance_record_methods_draft'),(0x64bf38,'thug_looping_sound_pending_methods_draft')]:exports.append([a,name])
for a,name in [(0x513630,'thug_local_net_create_draft'),(0x510f90,'thug_end_run_create_draft'),(0x4f9170,'thug_balance_component_create_draft'),(0x513ad0,'thug_looping_sound_create_draft')]:function_exports.append([a,name])
def tail_boundary(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);node=oracle.word(params+4)
 if oracle.word(node+8)!=0x5b512edc:return
 assert oracle.word(sp+8)!=0
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,cpu.reg_read(UC_X86_REG_ECX),1));cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,tail_boundary,begin=0x45ee20,end=0x45ee20)
registry=[(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280),(0xd8cc3428,0x4fbe20),(0x726e85aa,0x52a5c0),(0x7cd3e6d5,0x513630),(0xb1d5a3e1,0x510f90),(0x589e5fb3,0x4f9170),(0xb5f1e9d2,0x513ad0)]+[(int(c['type'],16),int(c['factory'],16)) for c in components]
local_chain=[0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58,0xd8cc3428,0x726e85aa,0x7cd3e6d5,0xb1d5a3e1,0x589e5fb3,0xb5f1e9d2,0x1859f772,0x4ff8dac6,0x408d2aa9,0x8bce7e66,0x380d909a]
remote_chain=[0x850eef66,0xd8cc3428,0x125044e2,0xb1d5a3e1,0xb5f1e9d2]
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,1,7,8,0xffffffff]):
 g=TailGraph(difficulty=(len(prefix_records)%3),toggle=(len(prefix_records)%2));g.symbol(0x78f80ec4,2,bits(.125));g.registry(registry)
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<3I',OBJ+0x14,0x77700000+len(prefix_records),2)
 stages=g.run([],f'original local/remote startup tail/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000;args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=1000000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+(local_chain if local&255 else remote_chain)+[0x18223fd6,0x488af07a]
 links={t:c for c,t in chain};assert oracle.word(OBJ+0x27c)==links[0x18223fd6]
 assert oracle.word(OBJ+0x28c)==(links[0x4ff8dac6] if local&255 else 0)
 overrides=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+8);assert oracle.word(oracle.word(overrides+4)+8)==heap_index
 params=oracle.word(BOUNDARY+4);assert oracle.word(oracle.word(params+4)+8)==0x5b512edc
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':oracle.word(DLOG),'expected_trap':True})
 oracle.counts['thug_skater_construct_startup_tail_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'overrides':overrides,'next_type':'0x5b512edc','diagnostics_mutate_id':mutate})
scope='Original local and remote skater startup continue through StateHistory and488af07a and allocate the actual heap-index QB overrides. Stop immediately before5b512edc tag/sticker image startup, which is not substituted. Parent582d90 remains partial with zero completion credit; no frame, cold boot, rendering or playable-level claim.'
finish('skater-startup-tail-parent',scope,{}, {**extra,'function_exports':function_exports,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,'memory_fixture':'skater-walk-memory.wasm','callback_counter':'startup_diagnostic_callbacks','native_callbacks':[{'module':'skater-startup-tail-diagnostic-fixture.wasm','export':'fixture_startup_print','slots':[DIAG+4]}]})
path=folder/'skater-startup-tail-parent-original.json';report=json.loads(path.read_text());code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records,'counted_complete':False};path.write_text(json.dumps(report,indent=2)+'\n');print('Partial constructor:',report['partial_constructor']['covered'],'/',len(code))
