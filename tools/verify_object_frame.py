import subprocess
"""Original object frame/notification graph and complete physics delegation."""
from pathlib import Path
prefix=Path('tools/verify_movement_dispatch.py').read_text().split('for mode in [0,1,2,3,4,5,6,0xffffffff]:')[0]
prefix=prefix.replace('movement-dispatch','object-frame')
exec(compile(prefix,'<complete movement graph>','exec'))
folder=ROOT/'local/validation/collision';report_path=folder.parent/'object-frame.json'
for row in [(0x45d920,'thug_object_update_components',0,'void',True,True,True),
 (0x45e4c0,'thug_object_mark_moved',1,'void',True,True,True),
 (0x474540,'thug_script_setup',4,'void',True,True,True)]:bind(*row)
FOTABLE,FCTABLE,FNODES,FPTABLE,FCONTEXT,FLOG=0x16d4000,0x16d4100,0x16d4200,0x16d4800,0x16d5000,0x16d7000
VIRTUAL=0x3f00d00
copy(FOTABLE,bytes(0x4000));put(FOTABLE+0x28,'<I',VIRTUAL)
put(FCTABLE+4,'<I',VIRTUAL);put(FCTABLE+0x24,'<I',VIRTUAL)
put(FPTABLE+4,'<I',0x510830)
fields.update([FOTABLE+0x28,FCTABLE+4,FCTABLE+0x24,FPTABLE+4])
function_exports += [[0x510830,'thug_component_physics_frame_bridge']]
virtual_calls=Counter()
def object_virtual(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);self=cpu.reg_read(UC_X86_REG_ECX)
 context=oracle.word(self+0x1c);log=oracle.word(context);owner=oracle.word(context+4);n=oracle.word(log);assert n<200
 oracle.setword(log,n+1)
 row=[self,oracle.word(owner+8),oracle.word(owner+0x104),oracle.word(owner+0x100),oracle.word(self+8),oracle.word(owner+0x58),oracle.word(context+0x14)]
 cpu.mem_write(log+4+n*28,struct.pack('<7I',*row));virtual_calls[hex(self)]+=1
 target=oracle.word(context+8)
 if target:
  width=oracle.word(context+16);assert width in [1,4]
  cpu.mem_write(target,oracle.word(context+12).to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.mem_write(VIRTUAL,b'\xc3');oracle.cpu.hook_add(UC_HOOK_CODE,object_virtual,begin=VIRTUAL,end=VIRTUAL)
ranges={0x45d920:106,0x45e4c0:52};frame_hits=Counter()
def frame_trace(cpu,at,size,user):frame_hits[at]+=1
for at,n in ranges.items():
 oracle.cpu.hook_add(UC_HOOK_CODE,frame_trace,begin=at,end=at+n-1)
 oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
ROOTS.add(0x45d920)
for at in [0x45d920,0x45d989]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
initial=bytes(memory);oracle.initial=initial
labels=[];oracle.cases.clear();oracle.counts.clear();oracle.coverage.clear()
def frame_compare(calls,p=(),changes=None,label='object frame'):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 retained_caches.clear()
 stages=oracle.case(calls,p,changes);labels.append(label);previous=0
 for step in stages:
  current=previous
  for address,data in step['outputs']:
   if address<=GOBS<address+len(data)//2:current=int.from_bytes(bytes.fromhex(data)[GOBS-address:GOBS-address+4],'little')
  step['callbacks']=current-previous;previous=current
 if retained_caches:stages[-1]['stack_objects']=list(retained_caches.values())
 return stages
def synthetic(flags=0,dead=0,count=3,suspended=0):
 p=[patch(BODIES,'<2I',FOTABLE,0),patch(BODIES+8,'<I',dead),patch(BODIES+0x10,'<I',0),patch(BODIES+0x1c,'<I',FCONTEXT),patch(BODIES+0x100,'<2I',FNODES if count else 0,flags),patch(BODIES+0x58,'<I',0x80000000)]
 for i in range(count+1):
  ctx=FCONTEXT+i*0x40;p += [patch(ctx,'<6I',FLOG,BODIES,0,0,4,i)]
  if i:
   node=FNODES+(i-1)*0x80
   p += [patch(node,'<5I',FCTABLE,0,suspended>>(i-1)&1,BODIES,node+0x80 if i<count else 0),patch(node+0x1c,'<I',ctx)]
 return p
for flags,dead,count in itertools.product([0,1,2,3,8,9,10,0xffffffff],[0,1,2],[0,3]):
 frame_compare([call(0x45d920,BODIES,[QUERY])]*2,synthetic(flags,dead,count),label='object suspend/script gates and final moved cleanup')
for mask in range(8):
 frame_compare([call(0x45d920,BODIES,[QUERY])],synthetic(suspended=mask),label='component suspend mask')
# Virtual methods replace the head, current next, object flags, or suspend a
# later component. Their complete log and mutations are compared on both sides.
for context,target,value in [(0,BODIES+0x100,0),(0,BODIES+0x100,FNODES+0x80),(0,BODIES+8,1),
 (1,FNODES+0x10,0),(1,FNODES+0x10,FNODES+0x100),(1,BODIES+8,1),
 (1,FNODES+0x80+8,1),(1,BODIES+0x104,0xffffffff),(2,BODIES+0x100,0)]:
 p=synthetic()+[patch(FCONTEXT+context*0x40+8,'<3I',target,value,4)]
 frame_compare([call(0x45d920,BODIES,[QUERY])],p,label='virtual callback changes live traversal')
for notify,count,mask in itertools.product([0,1,255,256,257,0xffffffff],[0,3],[0,7]):
 frame_compare([call(0x45e4c0,BODIES,[notify,QUERY])]*2,synthetic(0x80000001,count=count,suspended=mask),label='moved notification low byte and suspended components')
for context,target,value in [(1,FNODES+0x10,0),(1,FNODES+0x10,FNODES+0x100),(1,BODIES+0x104,0),(2,BODIES+0x100,0)]:
 frame_compare([call(0x45e4c0,BODIES,[1,QUERY])],synthetic()+[patch(FCONTEXT+context*0x40+8,'<3I',target,value,4)],label='notification mutates next and moved flag')
# Actual script setup/execution, with the established native QB observation
# callback changing fields before the component walk.
for target,value in [(BODIES+8,1),(BODIES+0x100,0),(BODIES+0x100,FNODES+0x80),(FNODES+8,1),(BODIES+0x104,8)]:
 b=Build();name=0x71235555;program(b,name)
 p=b.patches()+synthetic()+[patch(BODIES+0x10,'<I',SCRIPTS),patch(GOBS+4,'<4I',target,value,4,0)]
 frame_compare([call(0x4738e0,SCRIPTS),call(0x474540,SCRIPTS,[name,0,0,BODIES]),call(0x45d920,BODIES,[QUERY])],p,label='actual QB before component callbacks')
# Replay real movement fixtures through the original virtual component loop.
# Other components stay present for real lookups, but are suspended because
# their individual frame methods are not recovered in this checkpoint.
baseline=json.loads((ROOT/'local/validation/collision/movement-dispatch-fixtures.json').read_text())
fields.update(baseline['pointer_fields'])
chain=[];node=struct.unpack_from('<I',initial,BODIES+0x100-BASE)[0]
while node:
 assert node not in chain;chain.append(node);node=struct.unpack_from('<I',initial,node+0x10-BASE)[0]
assert PHYS in chain
for i in [*range(8),28,30,34,37,49,54]:
 old=baseline['cases'][i]
 calls=[(int(s['fn'],16),s['this'],s['args']) for s in old['steps'][:-1]]+[call(0x45d920,BODIES,[QUERY])]
 p=old['patches']+[patch(BODIES+0x104,'<I',2),patch(PHYS,'<I',FPTABLE),patch(PHYS+8,'<I',0)]
 p += [patch(at+8,'<I',1) for at in chain if at!=PHYS]
 changes={j:value for j,value in enumerate(old['globals'])}
 frame_compare(calls,p,changes,label='actual physics through component update, movement case '+str(i))
coverage={};pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
for at,n in ranges.items():
 rows=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in rows if not frame_hits[i.address]]
 coverage[hex(at)]={'total':len(rows),'covered':len(rows)-len(missing),'missing':missing}
scope='Complete45d920 object update and45e4c0 moved notification. Controlled virtual callbacks test ordering/mutations; actual QB runs before the list, and complete recovered510830 physics executes virtually across all six states, fixed/moving rails and training landings. Other component frame methods are suspended, not recovered or stubbed. No playable-level claim.'
fixture={'base':BASE,'memory':'object-frame-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE},{'module':'object-frame-callback.wasm','export':'fixture_object_step','original':VIRTUAL}]}
(folder/'object-frame-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(folder/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_coverage':dict(oracle.coverage),'instrumented_virtual_calls':dict(virtual_calls),'physics_component_chain':[hex(at) for at in chain],'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original object frame',len(labels),coverage,flush=True)

subprocess.run([str(ROOT/".tools/wasi-sdk-34.0-arm64-macos/bin/clang"),"--target=wasm32-unknown-unknown","-O2","-Wall","-Wextra","-Werror","-ffreestanding","-nostdlib","-Wl,--no-entry,--import-memory,--export-all,--global-base=33554432",str(ROOT/"tools/object_frame_callbacks.c"),"-o",str(folder/"object-frame-callback.wasm")],check=True)

subprocess.run(['node',str(ROOT/'tools/verify_object_frame_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/'object-frame-fixtures.json',folder/fixture['memory'],folder/'object-frame-callback.wasm',ROOT/'tools/object_frame_callbacks.c']}
(folder.parent/'object-frame.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS object-frame',report['cases'],sum(oracle.counts.values()))
