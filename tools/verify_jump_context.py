import hashlib,json,subprocess
"""Jump through real QB descriptors and scoped startup/object-frame entry."""
from pathlib import Path
prefix=Path('tools/verify_jump.py').read_text().split('for mode in [0,1,2,3,4,5,6,0xffffffff]:')[0]
exec(compile(prefix,'<verified jump runtime graph>','exec'))
for row in [(0x4750b0,'thug_component_execute_script',0,'word',True,True,True),
            (0x45d920,'thug_object_update_components',0,'void',True,True,True),
            (0x4738e0,'thug_script_initialize',0,'word',False,False,True),
            (0x474540,'thug_script_setup',4,'void',True,True,True)]:bind(*row)
CTABLE,OUTER_SCOPE=0x16dd800,0x16dd900
copy(CTABLE,bytes(0x200));put(CTABLE+0x28,'<I',0x5480a0)
event_member=struct.unpack('<I',pe.get_data(struct.unpack_from('<I',body_base)[0]-0x400000+0x14,4))[0]
put(CTABLE+0x14,'<I',event_member);fields.add(CTABLE+0x14)
function_exports.append([event_member,'thug_ui_object_event_bridge'])
put(OUTER_SCOPE,'<3I',QUERY,PRINT,ADAPTER)
fields.update([CTABLE+0x28,PHYS]);exports.append([0x64bc48,'thug_physics_methods'])
function_exports.append([0x5480a0,'thug_component_empty_frame_bridge'])
chain=[];node=struct.unpack_from('<I',memory,BODIES+0x100-BASE)[0]
while node:
 assert node not in chain;chain.append(node);node=struct.unpack_from('<I',memory,node+16-BASE)[0]
assert PHYS in chain
# Original collision-query globals are adapted only at the outer host boundary.
for at,size in [(0x4750b0,0x240),(0x45d920,106)]:
 ROOTS.add(at)
 returns=[i.address for i in md.disasm(pe.get_data(at-0x400000,size),at) if i.mnemonic=='ret']
 assert returns
 for address in [at,*returns]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=address,end=address)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear();qb_calls.clear();callback_counts.clear()
from collections import deque
recent=deque(maxlen=40)
def record_instruction(cpu,at,size,user):recent.append(at)
oracle.cpu.hook_add(UC_HOOK_CODE,record_instruction,begin=0x400000,end=0x630000)
for entry,mode,blocked,flags in itertools.product(['startup','object'],[0,1,4],[0,1],[[],[0xe13620a8],[0xec6b7fc7]]):
 b,_=jump_config()
 # First24-byte entry at6826c8, reconstructed from6417d0's initializer.
 descriptor=b.alloc(struct.pack('<6I',0x584cf9e9,0x5bd63b29,0x509a40,0,0,0));fields.add(descriptor+8)
 args=b''.join(b'\x16'+struct.pack('<I',flag) for flag in flags)
 code=b.alloc(b'\x01\x46'+struct.pack('<I',descriptor)+args+b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+8+len(args))
 name=0x71660003;b.symbol(name,7,code)
 cache_entry=b.alloc(struct.pack('<5I',name,code,1,0,0));slot=CACHETABLE+32+(name&3)*12
 # Preserve the final patched cache bucket, including Jump's event program.
 previous=next((bytes.fromhex(data) for at,data in reversed(b.extra) if at==slot),initial[slot-BASE:slot-BASE+12])
 link=b.alloc(previous);b.extra.append(patch(slot,'<3I',name,cache_entry,link))
 before,body=setup(False,0xbaf9b341)
 p=b.patches()+body+network()+[patch(BODIES,'<I',CTABLE),patch(BODIES+0x10,'<I',SCRIPTS),patch(BODIES+0x104,'<I',0),patch(PHYS,'<I',0x64bc48),patch(SKATER_STATE+0x18,'<I',mode),patch(PHYS+0x378,'<I',50),patch(GATE+0x26,'<B',blocked),patch(PHYS+0x2ec,'<B',0),patch(PHYS+0x94,'<I',0),patch(BODIES+0x4c,'<4f',25,10,30,1),patch(BODIES+0x5c,'<4f',25,10,30,1),patch(BODIES+0xac,'<4f',30,-20,40,1),patch(BODIES+0x6c,'<16f',*identity)]
 p += [patch(c+8,'<I',1) for c in chain]
 p += [patch(SKATER_STATE+off,'<B',0) for off in [0x20,0x30,0x40,0x48,0x78,0xa8,0xb0]]
 p += [patch(INPUT+0x20+i*0x20,'<B',0) for i in range(16)]
 calls=before+[call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[name,0,0,BODIES])]
 calls += [call(0x4750b0,SCRIPTS,[QUERY]) if entry=='startup' else call(0x45d920,BODIES,[QUERY])]
 try:stages=compare(calls,p,label=f'{entry} QB Jump descriptor state {mode}, blocked {blocked}, flags {flags}')
 except Exception:
  print('Context instruction tail',[(hex(at),next((i.mnemonic+' '+i.op_str for i in md.disasm(pe.get_data(at-0x400000,16),at)),'?')) for at in recent],flush=True)
  raise
 previous_audio=0
 for step in stages:
  current=previous_audio
  for at,data in step['outputs']:
   if at<=AUDIO_CONTEXT<at+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[AUDIO_CONTEXT-at:AUDIO_CONTEXT-at+4],'little')
   if len(data)==8 and int.from_bytes(bytes.fromhex(data),'little') in {item[0] for item in exports}:fields.add(at)
  step['callbacks']+=current-previous_audio;previous_audio=current
 assert oracle.word(GOBS)==1 and oracle.word(GOBS+64)==name
 assert oracle.word(SKATER_STATE+0x18)==(0 if mode==0 and blocked else 1)
scope='Host integration only, no additional recovered routines: actual QB opcode46 dispatches Jump through the original physics descriptor/member ABI from startup execution or object updates. Ground, airborne, rail, blocked, NoSound and alternate jump paths include real stat/state/sound/network dependencies. Other component frames are suspended in this fixture; native terminal QB and OS audio remain explicit observation boundaries. Null and valid outer host-service scopes are checked for restoration. This is not full descriptor registration or playable-level startup.'
fixture={'base':BASE,'memory':'jump-context-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_and_audio_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'scoped_event_services':{'symbol':'thug_component_services','pointer':0},'outer_scope':OUTER_SCOPE,'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]}
(folder/'jump-context-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'native_qb_calls':dict(qb_calls),'audio_device_calls':dict(callback_counts),'scope':scope}
(folder.parent/'jump-context.json').write_text(json.dumps(report,indent=2)+'\n');print('Original Jump context',len(labels),sum(oracle.counts.values()),flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_jump_context_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'jump-context-fixtures.json',folder/fixture['memory']]}
(folder.parent/'jump-context.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS jump-context',len(fixture['cases']),sum(oracle.counts.values()))
